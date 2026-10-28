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
3. Save a clearly named `待审核` draft in the private repository. Do not overwrite the user's intake file. Give the user the draft path and a concise summary of the decisions that need review.
4. Wait for the user's approval or corrections before creating or updating the final `problems/<slug>/` package or describing the problem as finalized. Apply corrections to the draft and request another review when needed.
5. Once approved, build the formal package from the public template, include confirmed statement, metadata, samples, reference solution, and appropriate verification. Run the repository checker plus problem-specific checks before reporting completion.

A structural check is not proof that a problem is correct. Examine sample answers, boundaries, algorithm complexity, and data coverage. Do not publish unpublished content to the public repository or a contest platform without the user's instruction.
