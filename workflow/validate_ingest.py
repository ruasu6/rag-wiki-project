#!/usr/bin/env python3
"""Reusable structural validators for the RAG Wiki ingestion workflow.

This tool validates files, hashes, Markdown links, dynamic section boundaries,
source registry metadata, and JSONL integrity. It does not replace semantic
review of source support, factual accuracy, or beginner suitability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


REQUIRED_LOG_FIELDS = {
    "run_id",
    "source_id",
    "node_id",
    "attempt",
    "timestamp",
    "status",
    "error_code",
    "validation_results",
    "repair_action",
}
MARKDOWN_LINK_RE = re.compile(r"\]\(([^)]+\.md(?:#[^)]*)?)\)")


class ValidationFailure(Exception):
    def __init__(self, failure_class: str, code: str, message: str) -> None:
        super().__init__(message)
        self.failure_class = failure_class
        self.code = code
        self.message = message


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def emit(payload: dict[str, Any], exit_code: int = 0) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


def ensure_file(path: Path) -> None:
    if not path.is_file():
        raise ValidationFailure(
            "METADATA_INCONSISTENCY",
            "FILE_NOT_FOUND",
            f"Required file does not exist: {path}",
        )


def check_markdown_links(root: Path, files: list[Path] | None = None) -> dict[str, Any]:
    if not root.is_dir():
        raise ValidationFailure(
            "VALIDATOR_INTERNAL_ERROR",
            "INVALID_LINK_ROOT",
            f"Markdown root is not a directory: {root}",
        )

    candidates = files if files is not None else sorted(root.glob("*.md"))
    checked_links: list[dict[str, str]] = []
    broken_links: list[dict[str, str]] = []

    for source_file in candidates:
        ensure_file(source_file)
        text = source_file.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            path_part = raw_target.split("#", 1)[0]
            target = (source_file.parent / path_part).resolve()
            item = {"source": str(source_file), "target": path_part}
            checked_links.append(item)
            if not target.is_file():
                broken_links.append(item)

    if broken_links:
        raise ValidationFailure(
            "WIKI_CONTENT_VALIDATION_FAILURE",
            "BROKEN_INTERNAL_LINK",
            f"Broken Markdown links: {broken_links}",
        )

    return {
        "files_checked": len(candidates),
        "links_checked": len(checked_links),
        "broken_links": 0,
    }


def verify_hash(path: Path, expected_hash: str) -> dict[str, Any]:
    ensure_file(path)
    actual_hash = sha256_file(path)
    if actual_hash != expected_hash:
        raise ValidationFailure(
            "METADATA_INCONSISTENCY",
            "SHA256_MISMATCH",
            f"SHA-256 mismatch for {path}: expected {expected_hash}, got {actual_hash}",
        )
    return {"path": str(path), "sha256": actual_hash}


def validate_marker_format(marker: str) -> None:
    if not marker.startswith("## ") or "\n" in marker or "\r" in marker:
        raise ValidationFailure(
            "VALIDATOR_INTERNAL_ERROR",
            "MARKER_FORMAT_INVALID",
            "A dynamic section marker must be one level-2 Markdown heading on one line.",
        )


def prefix_before_marker(path: Path, marker: str) -> tuple[bytes, int]:
    ensure_file(path)
    validate_marker_format(marker)
    data = path.read_bytes()
    marker_bytes = marker.encode("utf-8")
    pattern = re.compile(rb"(?m)^" + re.escape(marker_bytes) + rb"\r?$")
    matches = list(pattern.finditer(data))
    if not matches:
        raise ValidationFailure(
            "WIKI_CONTENT_VALIDATION_FAILURE",
            "SOURCE_MARKER_NOT_FOUND",
            f"Section marker not found: {marker}",
        )
    if len(matches) != 1:
        raise ValidationFailure(
            "WIKI_CONTENT_VALIDATION_FAILURE",
            "SOURCE_MARKER_AMBIGUOUS",
            f"Section marker must occur exactly once; found {len(matches)}: {marker}",
        )

    boundary = matches[0].start()
    prefix = data[:boundary]
    # A newly appended Markdown section normally adds one blank separator line.
    # Remove only that separator, preserving the baseline file's final newline.
    if prefix.endswith(b"\r\n\r\n"):
        prefix = prefix[:-2]
    elif prefix.endswith(b"\n\n"):
        prefix = prefix[:-1]
    else:
        raise ValidationFailure(
            "WIKI_CONTENT_VALIDATION_FAILURE",
            "SOURCE_MARKER_BOUNDARY_INVALID",
            "The marker is not separated from the preserved prefix by one blank line.",
        )
    return prefix, boundary


def check_prefix(path: Path, marker: str, expected_hash: str) -> dict[str, Any]:
    prefix, boundary = prefix_before_marker(path, marker)
    actual_hash = sha256_bytes(prefix)
    if actual_hash != expected_hash:
        raise ValidationFailure(
            "WIKI_CONTENT_VALIDATION_FAILURE",
            "PRESERVED_PREFIX_HASH_MISMATCH",
            f"Preserved prefix mismatch: expected {expected_hash}, got {actual_hash}",
        )
    return {
        "path": str(path),
        "marker": marker,
        "marker_byte_offset": boundary,
        "preserved_prefix_bytes": len(prefix),
        "preserved_prefix_sha256": actual_hash,
    }


def load_sources(path: Path) -> list[dict[str, Any]]:
    ensure_file(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValidationFailure(
            "METADATA_INCONSISTENCY",
            "SOURCES_JSON_NOT_ARRAY",
            "sources.json must contain a JSON array.",
        )
    return data


def check_source(
    sources_path: Path,
    source_id: str,
    raw_path: Path,
    expected_status: str,
) -> dict[str, Any]:
    sources = load_sources(sources_path)
    matches = [item for item in sources if item.get("source_id") == source_id]
    if len(matches) != 1:
        raise ValidationFailure(
            "METADATA_INCONSISTENCY",
            "SOURCE_ID_CARDINALITY",
            f"Expected exactly one {source_id} record; found {len(matches)}.",
        )
    record = matches[0]
    if record.get("status") != expected_status:
        raise ValidationFailure(
            "METADATA_INCONSISTENCY",
            "SOURCE_STATUS_MISMATCH",
            f"Expected {source_id} status {expected_status}, got {record.get('status')}.",
        )
    expected_hash = record.get("content_hash")
    if not isinstance(expected_hash, str) or not expected_hash:
        raise ValidationFailure(
            "METADATA_INCONSISTENCY",
            "CONTENT_HASH_MISSING",
            f"content_hash is missing for {source_id}.",
        )
    hash_result = verify_hash(raw_path, expected_hash)
    return {
        "source_id": source_id,
        "status": record.get("status"),
        "retrieved_at": record.get("retrieved_at"),
        "ingested_at": record.get("ingested_at"),
        **hash_result,
    }


def jsonl_records(path: Path) -> list[dict[str, Any]]:
    ensure_file(path)
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationFailure(
                "METADATA_INCONSISTENCY",
                "JSONL_PARSE_ERROR",
                f"Invalid JSONL at line {line_number}: {exc}",
            ) from exc
        missing = sorted(REQUIRED_LOG_FIELDS - set(record))
        if missing:
            raise ValidationFailure(
                "METADATA_INCONSISTENCY",
                "JSONL_REQUIRED_FIELDS_MISSING",
                f"Line {line_number} is missing fields: {missing}",
            )
        records.append(record)
    return records


def check_log_prefix(path: Path, lines: int, expected_hash: str) -> dict[str, Any]:
    ensure_file(path)
    raw_lines = path.read_bytes().splitlines(keepends=True)
    if lines < 1 or len(raw_lines) < lines:
        raise ValidationFailure(
            "VALIDATOR_INTERNAL_ERROR",
            "INVALID_LOG_PREFIX_LENGTH",
            f"Cannot hash {lines} lines from a {len(raw_lines)}-line log.",
        )
    prefix = b"".join(raw_lines[:lines])
    actual_hash = sha256_bytes(prefix)
    if actual_hash != expected_hash:
        raise ValidationFailure(
            "METADATA_INCONSISTENCY",
            "LOG_PREFIX_HASH_MISMATCH",
            f"Log prefix mismatch: expected {expected_hash}, got {actual_hash}",
        )
    return {"path": str(path), "lines": lines, "sha256": actual_hash}


def expect_failure(callback: Any, expected_code: str) -> bool:
    try:
        callback()
    except ValidationFailure as exc:
        return exc.code == expected_code
    return False


def self_check(script_path: Path) -> dict[str, Any]:
    results: dict[str, bool] = {}
    with tempfile.TemporaryDirectory(prefix="rag-validator-self-check-") as tmp:
        root = Path(tmp)
        (root / "a.md").write_text("# A\n", encoding="utf-8")
        (root / "b.md").write_text("# B\n", encoding="utf-8")
        (root / "single-valid.md").write_text("[A](a.md)\n", encoding="utf-8")
        (root / "multi-valid.md").write_text(
            "[A](a.md) and [B](b.md)\n\n[A again](a.md)\n", encoding="utf-8"
        )
        (root / "broken.md").write_text("[Missing](missing.md)\n", encoding="utf-8")

        results["valid_markdown_link"] = check_markdown_links(
            root, [root / "single-valid.md"]
        )["broken_links"] == 0
        results["multiple_and_multiline_links"] = check_markdown_links(
            root, [root / "multi-valid.md"]
        )["links_checked"] == 3
        results["broken_markdown_link_rejected"] = expect_failure(
            lambda: check_markdown_links(root, [root / "broken.md"]),
            "BROKEN_INTERNAL_LINK",
        )

        payload = root / "payload.txt"
        payload.write_bytes(b"known payload\n")
        expected_hash = sha256_file(payload)
        results["sha256_match"] = verify_hash(payload, expected_hash)["sha256"] == expected_hash
        results["sha256_mismatch_rejected"] = expect_failure(
            lambda: verify_hash(payload, "0" * 64), "SHA256_MISMATCH"
        )

        baseline = b"# Existing Wiki\n"
        merged = root / "merged.md"
        marker = "## S99 補充"
        merged.write_bytes(baseline + b"\n" + marker.encode("utf-8") + b"\n\nNew content.\n")
        prefix_result = check_prefix(merged, marker, sha256_bytes(baseline))
        results["dynamic_section_boundary"] = (
            prefix_result["preserved_prefix_bytes"] == len(baseline)
        )
        results["missing_marker_rejected"] = expect_failure(
            lambda: prefix_before_marker(merged, "## Missing"),
            "SOURCE_MARKER_NOT_FOUND",
        )
        results["malformed_marker_rejected"] = expect_failure(
            lambda: prefix_before_marker(merged, "S99 補充"),
            "MARKER_FORMAT_INVALID",
        )
        duplicate = root / "duplicate.md"
        duplicate.write_text(
            f"# Root\n\n{marker}\n\nOne\n\n{marker}\n\nTwo\n", encoding="utf-8"
        )
        results["duplicate_marker_rejected"] = expect_failure(
            lambda: prefix_before_marker(duplicate, marker),
            "SOURCE_MARKER_AMBIGUOUS",
        )

        probe = subprocess.run(
            [sys.executable, str(script_path), "_probe-fail"],
            check=False,
            capture_output=True,
            text=True,
        )
        results["exit_code_propagation"] = probe.returncode == 7

    failed = sorted(name for name, passed in results.items() if not passed)
    if failed:
        raise ValidationFailure(
            "VALIDATOR_INTERNAL_ERROR",
            "VALIDATOR_SELF_CHECK_FAILED",
            f"Self-check failures: {failed}",
        )
    return {"tests": results, "tests_passed": len(results), "tests_failed": 0}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("self-check", help="Run validator fixtures and exit-code checks.")
    subparsers.add_parser("_probe-fail", help=argparse.SUPPRESS)

    links = subparsers.add_parser("check-links", help="Validate Markdown links in a directory.")
    links.add_argument("--root", type=Path, required=True)

    source = subparsers.add_parser("check-source", help="Validate source metadata and raw hash.")
    source.add_argument("--sources", type=Path, required=True)
    source.add_argument("--source-id", required=True)
    source.add_argument("--raw", type=Path, required=True)
    source.add_argument("--expected-status", required=True)

    prefix = subparsers.add_parser("check-prefix", help="Validate content preserved before a marker.")
    prefix.add_argument("--merged", type=Path, required=True)
    prefix.add_argument("--marker", required=True)
    prefix.add_argument("--expected-prefix-hash", required=True)

    log = subparsers.add_parser("check-jsonl", help="Validate execution-log JSONL structure.")
    log.add_argument("--log", type=Path, required=True)

    log_prefix = subparsers.add_parser(
        "check-log-prefix", help="Validate an immutable prefix of a JSONL log."
    )
    log_prefix.add_argument("--log", type=Path, required=True)
    log_prefix.add_argument("--lines", type=int, required=True)
    log_prefix.add_argument("--expected-hash", required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    script_path = Path(__file__).resolve()
    try:
        if args.command == "_probe-fail":
            return 7
        if args.command == "self-check":
            result = self_check(script_path)
        elif args.command == "check-links":
            result = check_markdown_links(args.root)
        elif args.command == "check-source":
            result = check_source(
                args.sources, args.source_id, args.raw, args.expected_status
            )
        elif args.command == "check-prefix":
            result = check_prefix(
                args.merged, args.marker, args.expected_prefix_hash
            )
        elif args.command == "check-jsonl":
            records = jsonl_records(args.log)
            result = {
                "path": str(args.log),
                "records": len(records),
                "source_ids": sorted({record["source_id"] for record in records}),
            }
        elif args.command == "check-log-prefix":
            result = check_log_prefix(args.log, args.lines, args.expected_hash)
        else:
            raise AssertionError(f"Unhandled command: {args.command}")
    except ValidationFailure as exc:
        return emit(
            {
                "status": "FAIL",
                "failure_class": exc.failure_class,
                "error_code": exc.code,
                "message": exc.message,
            },
            1,
        )
    except Exception as exc:  # Defensive boundary: classify tool failures separately.
        return emit(
            {
                "status": "FAIL",
                "failure_class": "VALIDATOR_INTERNAL_ERROR",
                "error_code": "UNEXPECTED_VALIDATOR_EXCEPTION",
                "message": f"{type(exc).__name__}: {exc}",
            },
            2,
        )

    return emit({"status": "PASS", "result": result}, 0)


if __name__ == "__main__":
    raise SystemExit(main())
