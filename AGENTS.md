# Project context

## Procedure extraction investigation

- The active feature is issue #3, on branch `feat/3-c-plugin-registration-poc`.
- The intended longer-term goal is to extract C plug-in procedure metadata by
  compiling the plug-ins and capturing their registration behavior, ideally
  with a lightweight collector rather than parsing C source. It is not yet
  established whether this can run without GIMP's normal plug-in host/runtime.
- Do not confuse that goal with querying the live PDB. A wildcard query can
  enumerate procedures after GIMP has loaded them, but does not intercept
  registration calls or prove that a separate lightweight host is feasible.
- A current POC in `scripts/capture_pdb_poc.py` queries every procedure from
  the live PDB and writes metadata to JSON. This is an exploratory way to check
  what metadata the PDB exposes, not the settled architecture or production
  catalog integration.
- The user verified that this works in their GIMP Flatpak to list procedure
  names with `Gimp.get_pdb().query_procedures(".*", ... eight wildcard
  filters ...)`. The metadata export still needs to be run and inspected.
- Script-Fu's `gimp-pdb-query` was not callable in the user's Flatpak session.
  Do not suggest it as the working enumeration method. Script-Fu legacy
  boolean output can appear as `(0)`; in that specific wrapper it represents
  integer false, even though a non-empty Scheme list is itself truthy.
- The user has no need to create a custom container image for CI. If a CI
  workflow is pursued, building GIMP from source in the workflow remains an
  option; first assess the required runtime and feasibility.

## Current working files

- `scripts/capture_pdb_poc.py`: all-procedure live-PDB metadata export.
- `Makefile`: `pdb-poc` target for a locally installed GIMP CLI.
- `documentation/procedure-extraction-poc.md`: current POC notes and Flatpak
  invocation. Keep it in `documentation/`.
- The live export has not been validated in this workspace because no GIMP
  executable is installed here. The user can run the documented Flatpak
  command and share `tmp/pdb-poc.json` for inspection.
- Keep this spike separate from `scripts/build_pdb.py`; do not add a static C
  source scanner as a substitute for executing registration behavior.

## Approved program document change control

- Treat `documentation/plan/program.md` version 1.0 as the approved, generally
  static statement of the project's goals and direction.
- Do not change, reformat, or update that document unless the user explicitly
  approves a specific change to it. The approval must clearly state both why
  the change is needed and what content or scope should change. A general
  request to work on the project or a phase plan is not approval to revise the
  program document.
- If the reason or requested change is unclear, ask the user to clarify before
  editing the program document.
- For every approved change, update the document's version and add a
  `Version history` entry recording the version, date, change summary, and
  reason. Do not infer approval or silently revise program goals while
  implementing another task.

## Phase and progress documentation

- Follow the project-local [contributing progress guide](CONTRIBUTING-PROGRESS.md)
  when updating phase plans or recording scope changes.
- Phase 1 remains `in development` until its completion criteria are met.
  Keep its plan accurate as POCs and findings evolve; do not treat a draft
  Phase 2 plan as evidence that Phase 1 is complete.

## Phase 1 branch workflow

- `feat/1-add-missing-pdb-procedures` is the Phase 1 root/integration branch,
  based on `main`. Create each Phase 1 issue or feature branch from this root
  branch, rather than branching from `main` or stacking one Phase 1 feature
  branch on another.
- Target Phase 1 work pull requests at `feat/1-add-missing-pdb-procedures`.
  Once Phase 1 is complete, the root branch can be proposed for integration
  into `main`.
- The current issue #3 branch, `feat/3-c-plugin-registration-poc`, is a child
  of the Phase 1 root branch.

## GitHub CLI handoff

- When a task requires a GitHub operation and the available `gh` CLI is not
  authenticated for the agent, provide the exact non-interactive `gh`
  command(s) as copyable code examples for the user to run in their terminal.
- The user can execute those commands and share the output for follow-up.
  Do not treat the agent's missing authentication as a reason to omit the
  operation or to imply that the user cannot use `gh`.
