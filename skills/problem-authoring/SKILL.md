---
name: problem-authoring
description: Draft and revise algorithm contest problems from user notes, including incomplete intake forms, while keeping unpublished problems private and waiting for user review before finalizing.
---

# Problem authoring

Use this skill when the user asks to develop or revise an algorithm contest problem for the Problem Forge repositories.

## Repository roles

- `problem-forge` holds reusable templates, checks, and public process guidance.
- `problem-forge-private` holds unpublished problem material. Keep draft statements, solutions, and data there.
- Find the current repository paths rather than assuming a fixed parent directory.

## From partial notes to a reviewable draft

1. Read the user's filled file and preserve every explicit requirement. Treat empty fields as open choices, not as permission to claim they were specified.
2. Make reasonable, coherent proposals for missing title, statement, constraints, samples, solution, and validation plan. Mark proposed values and unresolved choices clearly. If too little is provided to infer a unique problem, choose one concrete candidate that matches the supplied difficulty and topics instead of stopping at a questionnaire.
3. Keep sample explanations focused on the stated sample result. Put solution branches, edge-case reasoning, and common mistakes in solution or validation notes, not in sample explanations. Prepare multiple distinct test cases, including minimum and maximum constraints and relevant boundaries; distinguish multiple test files from a multi-case input format with `T`.
   When the input format already specifies the complete input, do not add a redundant "single test case" or "仅一组数据" sentence to the statement.
   Every final contest statement must show the input source, output destination, time limit, and memory limit. Read time and memory values from `problem.json` or the confirmed judge configuration; never silently omit or invent them. Before packaging, compare the rendered statement against that configuration and check that all four fields are visible.
   When a visual reference is supplied, reproduce its meaningful hierarchy and alignment, including header, title, bold section headings, indentation, and bordered sample input/output table. Render and inspect the final PDF rather than relying on source text alone.
4. Save a clearly named `待审核` draft in the private repository. Do not overwrite the user's intake file. Give the user the draft path and a concise summary of the decisions that need review.
5. Wait for the user's approval or corrections before creating or updating the final `problems/<slug>/` package or describing the problem as finalized. Apply corrections to the draft and request another review when needed.
6. Once approved, build the formal package in the private repository. For this 2026 freshman contest, follow [Hydro package structure](references/hydro-package.md). Keep source, solutions, and validation tools in the internal workspace; export only the files listed for Hydro. Verify all prepared tests and cross-check correct solutions before reporting completion.
7. After the user approves the statement and other review items, and the Hydro package is complete and verified, check whether the private repository has a GitHub remote. If it does, commit and push the finished problem package to that private repository, then verify the remote contains the commit and report its link. Do not push drafts awaiting review or unpublished material to a public repository. If no remote is linked or the push fails, report that the package remains local.

A structural check is not proof that a problem is correct. Examine sample answers, boundaries, algorithm complexity, and data coverage. Do not publish unpublished content to the public repository or a contest platform without the user's instruction.
