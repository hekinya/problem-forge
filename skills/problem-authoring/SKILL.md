---
name: problem-authoring
description: Develop algorithm contest problems through interactive intake, user review of complete key information, statement authoring, and verified private packaging.
---

# Problem authoring

Use this skill when the user asks to develop or revise an algorithm contest problem for the Problem Forge repositories.

## Repository roles

- `problem-forge` holds reusable templates, checks, and public process guidance.
- `problem-forge-private` holds unpublished problem material. Keep draft statements, solutions, and data there.
- Find the current repository paths rather than assuming a fixed parent directory.

## Statement typesetting

Before the first XCPC build in a checkout, read the installation section in [XCPC workflow](references/xcpc-generator.md). Proactively run `python tools/setup_xcpc.py --check`; if dependencies are absent or invalid on supported Windows x64, run `python tools/setup_xcpc.py` to install/repair them locally, then repeat `--check`. Do not require a user-provided archive or manual installation. Installation must pass its sample-PDF smoke test before rendering contest material. Respect actual environment permission restrictions; never report successful installation after a failed command.

Use the [XCPC command-line workflow](references/xcpc-generator.md) for new PDF builds: project sources → shared converter → pinned Typst template → native Typst → PDF. No browser, npm, or manual JSON import is required. Keep `statement.md` as canonical prose, `problem.json` as judge limits, and sample files as sample data. Render and inspect every final PDF before Hydro packaging. The browser editor remains optional for visual exploration.

The older [Pandoc/LaTeX workflow](references/statement-typesetting.md) remains available for reproducing earlier outputs or when explicitly selected. Do not mix styles within a contest. An explicit reformatting request for an approved problem authorizes rendering without repeating intake; preserve approved meaning. When trialing a new backend, save comparison PDFs separately before replacing formal packages.

## Interactive intake and review before statement authoring

1. Start from the conversation, supplied references, and existing project decisions. List the key problem information and ask the user concise questions about what is missing; do not require the user to fill in a file. Cover title and identifier, contest/platform, difficulty and topics, core task, input/output rules, constraints and special cases, samples, time/memory limits, statement format, and privacy. Reuse already explicit answers rather than asking again.
2. After the user's response, fill in information they did not explicitly answer using the available context and coherent AI proposals. Preserve explicit requirements and clearly distinguish user-confirmed information from AI-proposed values. Present the complete key-information sheet to the user for review, and save it as a clearly named `关键信息-待审核` file in the private repository. Wait for explicit approval or corrections before drafting or rendering the statement; silence or an incomplete reply is not approval. Apply corrections and resubmit the complete information when necessary. Do not invent a contest-assigned Hydro PID; leave it pending until confirmed before export.
3. Keep sample explanations focused on the stated sample result. Put solution branches, edge-case reasoning, and common mistakes in solution or validation notes, not in sample explanations. Prepare multiple distinct test cases, including minimum and maximum constraints and relevant boundaries; distinguish multiple test files from a multi-case input format with `T`.
   When the input format already specifies the complete input, do not add a redundant "single test case" or "仅一组数据" sentence to the statement.
   Every final contest statement must show the input source, output destination, time limit, and memory limit. Read time and memory values from `problem.json` or the confirmed judge configuration; never silently omit or invent them. Before packaging, compare the rendered statement against that configuration and check that all four fields are visible.
   When a visual reference is supplied, reproduce its meaningful hierarchy and alignment, including header, title, bold section headings, indentation, and bordered sample input/output table. Render and inspect the final PDF rather than relying on source text alone.
4. Once the key information is approved, write the statement and save a clearly named `题面-待审核` draft in the private repository. Do not overwrite user-supplied files. Give the user the draft path and a concise summary of the decisions that need review.
5. Wait for the user's approval or corrections before creating or updating the final `problems/<slug>/` package or describing the problem as finalized. Apply corrections to the draft and request another review when needed.
6. Once approved, build the formal package in the private repository. For this 2026 freshman contest, follow [Hydro package structure](references/hydro-package.md). Keep source, solutions, and validation tools in the internal workspace; export only the files listed for Hydro. Verify all prepared tests and cross-check correct solutions before reporting completion.
7. After the user approves the statement and other review items, and the Hydro package is complete and verified, check whether the private repository has a GitHub remote. If it does, commit and push the finished problem package to that private repository, then verify the remote contains the commit and report its link. Do not push drafts awaiting review or unpublished material to a public repository. If no remote is linked or the push fails, report that the package remains local.

A structural check is not proof that a problem is correct. Examine sample answers, boundaries, algorithm complexity, and data coverage. Do not publish unpublished content to the public repository or a contest platform without the user's instruction.
