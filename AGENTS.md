
# RAG Learning Wiki Project

## 1. Project Goal
Build an LLM-powered knowledge Wiki about Retrieval-Augmented Generation (RAG), then generate an educational HTML presentation based on the Wiki.

The project must:
- Ingest at least 5 independent, verifiable source documents.
- Use discussion-first, generation-second workflow.
- Build interconnected Wiki pages.
- Generate an HTML presentation for beginners.
- Document the workflow graph, loops, validation and revisions.
- Produce an evidence-based reflection after execution.

## 2. Project Structure
- raw/: Original source documents and metadata.
- wiki/: Generated knowledge pages and source references.
- slides/: HTML presentation and required assets.
- workflow/: Graph design, validation results and execution logs.

## 3. Working Rules
1. Discuss and propose a plan before generating files.
2. Never fabricate sources, citations, quotations, or execution results.
3. Track the original URL, title and retrieval date for each source.
4. Distinguish original source content from AI-generated summaries.
5. Keep citations traceable from the Wiki to source documents.
6. Do not generate the presentation until Wiki validation passes.
7. Record validation failures and correction attempts.
8. Preserve existing files unless modifications are explicitly requested.
9. Write instructional content in Traditional Chinese (Taiwan).
10. Explain changes and verification results after each task.

## 4. Ingestion Workflow
For each source:
1. Check source accessibility and credibility.
2. Extract and normalize its content.
3. Identify key concepts and definitions.
4. Generate or update relevant Wiki pages.
5. Add source references and cross-links.
6. Validate coverage, accuracy and citation traceability.
7. Retry failed steps with documented reasons.

A document is counted as ingested only after its content is incorporated into the Wiki and validation passes.

## 5. Presentation Requirements
- Create a self-contained, browser-readable HTML presentation.
- Target readers unfamiliar with RAG.
- Explain concepts progressively with examples and diagrams.
- Use the validated Wiki as the primary knowledge source.
- Avoid unsupported claims.
- Verify that slide content matches the Wiki.
- Keep the presentation readable on desktop and mobile.

## 6. Workflow and Reflection
Maintain records of:
- Node inputs and outputs.
- Validation outcomes.
- Failed attempts and fixes.
- Retry counts.
- Changes to the workflow graph.
- Final execution evidence.

Do not invent reflection results before running the workflow.

## 7. Current Phase
Phase 1: Project initialization and Wiki planning.

Do not ingest sources or generate slides until the user approves the source selection and Wiki structure.
