#!/usr/bin/env python3
"""Repeatable structural validator for the self-contained HTML slide deck.

This checks markup structure, slide navigation hooks, inline JavaScript syntax,
Wiki references, and registered source IDs. It does not replace browser visual
QA or semantic review against the Wiki.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path


class DeckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[dict[str, str]] = []
        self.ids: set[str] = set()
        self.local_links: list[str] = []
        self.scripts: list[str] = []
        self._in_script = False
        self._script_parts: list[str] = []
        self.lang: str | None = None
        self.has_main = False
        self.has_nav = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.lang = values.get("lang")
        if tag == "main":
            self.has_main = True
        if tag == "nav":
            self.has_nav = True
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "section" and "slide" in values.get("class", "").split():
            self.slides.append(values)
        if tag == "a" and values.get("href", "").startswith("../wiki/"):
            self.local_links.append(values["href"])
        if tag == "script" and not values.get("src"):
            self._in_script = True
            self._script_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._script_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_script:
            self.scripts.append("".join(self._script_parts))
            self._in_script = False


def add_check(checks: list[dict[str, object]], name: str, passed: bool, evidence: object) -> None:
    checks.append({"check": name, "status": "PASS" if passed else "FAIL", "evidence": evidence})


def validate(root: Path, html_path: Path) -> tuple[int, dict[str, object]]:
    checks: list[dict[str, object]] = []
    parser = DeckParser()
    text = html_path.read_text(encoding="utf-8")
    parser.feed(text)

    add_check(checks, "semantic_structure", parser.has_main and parser.has_nav and parser.lang == "zh-Hant-TW", {"main": parser.has_main, "nav": parser.has_nav, "lang": parser.lang})
    add_check(checks, "slide_count", len(parser.slides) == 10, len(parser.slides))
    expected_ids = {f"slide-{number}" for number in range(1, 11)}
    actual_slide_ids = {slide.get("id", "") for slide in parser.slides}
    add_check(checks, "slide_ids", actual_slide_ids == expected_ids, sorted(actual_slide_ids))

    navigation_ids = {"prevButton", "nextButton", "pageStatus", "progressBar"}
    add_check(checks, "navigation_hooks", navigation_ids.issubset(parser.ids), sorted(navigation_ids & parser.ids))
    navigation_logic = all(token in text for token in ["ArrowLeft", "ArrowRight", "goTo(current - 1)", "goTo(current + 1)"])
    add_check(checks, "navigation_logic_present", navigation_logic, "keyboard and button handlers")

    scripts_ok = bool(parser.scripts)
    script_evidence: list[dict[str, object]] = []
    node = shutil.which("node")
    osascript = shutil.which("osascript")
    if node:
        for index, script in enumerate(parser.scripts, 1):
            with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as handle:
                handle.write(script)
                handle.flush()
                result = subprocess.run(["node", "--check", handle.name], capture_output=True, text=True, check=False)
            script_evidence.append({"script": index, "engine": "node --check", "exit_code": result.returncode, "stderr": result.stderr.strip()})
            scripts_ok = scripts_ok and result.returncode == 0
    elif osascript:
        for index, script in enumerate(parser.scripts, 1):
            expression = f"new Function({json.dumps(script)});"
            result = subprocess.run([osascript, "-l", "JavaScript", "-e", expression], capture_output=True, text=True, check=False)
            script_evidence.append({"script": index, "engine": "JavaScriptCore new Function", "exit_code": result.returncode, "stderr": result.stderr.strip()})
            scripts_ok = scripts_ok and result.returncode == 0
    else:
        scripts_ok = False
        script_evidence.append({"error": "no supported JavaScript syntax engine; browser validation required"})
    add_check(checks, "javascript_syntax", scripts_ok, script_evidence)

    missing_links: list[str] = []
    for href in parser.local_links:
        target = (html_path.parent / href).resolve()
        if not target.is_file() or root.resolve() not in target.parents:
            missing_links.append(href)
    add_check(checks, "wiki_links", not missing_links and bool(parser.local_links), {"checked": len(parser.local_links), "missing": missing_links})

    registry = json.loads((root / "sources.json").read_text(encoding="utf-8"))
    registered = {item["source_id"] for item in registry if item.get("status") == "INGESTED"}
    source_errors: list[dict[str, object]] = []
    wiki_errors: list[dict[str, object]] = []
    for index, slide in enumerate(parser.slides, 1):
        sources = {item.strip() for item in slide.get("data-sources", "").split(",") if item.strip()}
        wikis = {item.strip() for item in slide.get("data-wiki", "").split(",") if item.strip()}
        unknown = sorted(sources - registered)
        missing_wikis = sorted(name for name in wikis if not (root / "wiki" / name).is_file())
        if not sources or unknown:
            source_errors.append({"slide": index, "unknown_or_empty": unknown or ["EMPTY"]})
        if not wikis or missing_wikis:
            wiki_errors.append({"slide": index, "missing_or_empty": missing_wikis or ["EMPTY"]})
    add_check(checks, "slide_source_ids", not source_errors, source_errors or "all slide source IDs are INGESTED")
    add_check(checks, "slide_wiki_mapping", not wiki_errors, wiki_errors or "all slide Wiki mappings exist")

    no_external = not re.search(r"<(?:script|link|img)\b[^>]+(?:src|href)=[\"']https?://", text, flags=re.I)
    add_check(checks, "self_contained_resources", no_external, "no remote script, stylesheet, or image resources")
    add_check(checks, "accessibility_hooks", all(token in text for token in ["aria-live", "aria-roledescription", "prefers-reduced-motion", ":focus-visible"]), "live region, slide roles, reduced motion, focus styling")

    passed = all(item["status"] == "PASS" for item in checks)
    result: dict[str, object] = {
        "status": "PASS" if passed else "FAIL",
        "html": str(html_path.relative_to(root)),
        "checks": checks,
        "manual_review_required": [
            "desktop and mobile visual layout",
            "real-browser keyboard and button interaction",
            "semantic fidelity to Wiki and beginner suitability",
        ],
    }
    return (0 if passed else 1), result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--html", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    html_path = (args.html or root / "slides" / "index.html").resolve()
    try:
        code, result = validate(root, html_path)
    except Exception as error:  # Validator failure must be distinguishable from content failure.
        print(json.dumps({"status": "ERROR", "error_code": "VALIDATOR_INTERNAL_ERROR", "detail": str(error)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
