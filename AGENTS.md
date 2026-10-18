# Project context

## Procedure extraction investigation

- The active feature is issue #3, on branch `feat/1-add-missing-pdb-procedures`.
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
