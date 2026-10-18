# Phase 1: C Procedure Extraction — Plan

Status: scoped and approved by the project owner (developer + plugin authors audience). This plan is a Phase 1 blueprint to prototype, validate, and integrate C-registered procedures into the existing GIMP Procedure Browser site.

Goals

- Prototype a collector that captures procedure registration metadata for both native `app/pdb` procedures and built-in C plug-ins.
- Produce a repeatable extraction script that emits a versioned JSON catalog for a specific GIMP stable revision.
- Validate the extractor in CI (Ubuntu) and integrate the resulting catalog into the website only after validation passes.
- Produce a coverage report and document known limitations.

Scope

- In-scope: Native `app/pdb` C procedures and built-in C plug-in procedures as observed in a standard Ubuntu CI/runtime environment. The extractor should capture all safely observable registration metadata.
- Out-of-scope: Third-party plug-ins, environment-conditional procedures not present in the standard CI runtime, and historical catalogs (the site will publish only the current stable revision).

Deliverables

1. Documented local development and build instructions for the prototype collector (Ubuntu-focused).
2. A repeatable extraction command or script that produces a versioned JSON catalog (including the GIMP revision used).
3. A JSON schema and validation checks for the produced catalog.
4. CI job(s) that run on ubuntu-latest, check the upstream stable revision daily, and: if changed, run extraction, validate output, and publish the site only on success.
5. Integration work in the static site to display extracted C-procedure fields (parameters, return values, menu paths, file-format metadata, and source links where available).
6. A coverage report and a documented list of limitations and environment-dependent gaps.

Approach and experiments

This phase emphasizes prototyping to test the central hypothesis: a lightweight stub/collector can capture C registration calls sufficiently to build the catalog without needing a full GIMP runtime in CI.

Planned experiments

- E1: libgimp stub for built-in C plug-ins
  - Create a minimal libgimp implementation exposing the subset of APIs that C plug-ins call during registration (gimp_procedure_new and friends, gimp_procedure_set_menu_label, gimp_procedure_add_menu_path, gimp_procedure_add_argument, gimp_procedure_add_return_value, etc.).
  - Compile one or two representative plug-ins against the stub and run them in a collector harness that records registration calls into JSON.
  - Evaluate how many plug-ins register successfully and whether the recorded metadata matches expectations.

- E2: native `app/pdb` registration capture
  - Prototype a lightweight harness that can link and run code that would call the native registration APIs (for example, by compiling a collector binary against the same interfaces used in app/pdb files or by adapting native app/pdb compilation units into a collector harness).
  - Capture at least one representative native PDB procedure and evaluate the completeness of metadata.

- E3: Compare to live GIMP (optional feasibility test)
  - Locally (or in CI only if feasible), build a normal GIMP runtime for a chosen stable revision and run the existing live-PDB POC (scripts/capture_pdb_poc.py) to produce a reference JSON.
  - Compare the lightweight collector output against the full-GIMP output for a small representative set to measure coverage and fidelity.

Validation and acceptance

Create a validation checklist and automated checks that must pass before replacing the live catalog:

- JSON schema validation (required fields, types)
- Basic coverage checks: presence of a set of known, high-confidence procedures (e.g., a shortlist of common native and plug-in procedures expected in that stable revision)
- No unexpected empty records or malformed parameter lists
- Source link and provenance metadata present (GIMP revision used)

If validation fails, the CI run must fail and the site must keep the previous live catalog.

Integration

- Update the data schema used by the static site to accept the full set of collected C fields. Maintain backward compatibility for existing Script-Fu entries.
- UI adjustments: present additional sections for arguments/return-values and file-format metadata. Ensure graceful handling when fields are absent.

CI and publishing

- A daily job checks the GIMP stable channel for a new revision. Only when the stable revision changes will the CI attempt a full extraction run.
- The CI job runs on `ubuntu-latest` and performs:
  1. Checkout the repository
  2. Fetch the GIMP stable source for the revision under test
  3. Run the prototype collector(s) (stub-based) and produce data/pdb.json
  4. Validate the output with JSON schema and coverage checks
  5. If validation passes, build the static site and deploy to GitHub Pages (replacing the live catalog)
  6. If validation fails, fail the job and leave the live site unchanged

Note: If prototype evidence shows the stub approach cannot reach sufficient coverage, CI may optionally build a full GIMP runtime on ubuntu-latest for validation. This is a cost/complexity decision to be made after the prototype experiments.

Risks and mitigations

- Risk: A single stub cannot capture both registration families.
  - Mitigation: Prototype one representative example from each family. If separate collectors are required, normalize outputs into a single catalog during integration.

- Risk: Environment-dependent registrations (external deps) will be missing from the CI catalog.
  - Mitigation: Document these as limitations in the coverage report and treat CI output as the canonical set for the standard runtime.

- Risk: CI build of full GIMP is time-consuming or fragile.
  - Mitigation: Use local builds for deep validation and keep CI limited to stub-based extraction unless the prototype shows otherwise.

Timeline and milestones (tentative)

- Week 1: Prototype libgimp stub and collector for one built-in plug-in (E1). Produce first JSON sample and coverage notes.
- Week 2: Prototype native `app/pdb` capture (E2) and capture a representative native procedure. Produce combined sample and a short comparison report.
- Week 3: Define JSON schema, write validation checks, and adapt the website schema/UI to render new fields (preview only).
- Week 4: Add CI job that runs extraction, validates output, and produces a preview artifact. If everything passes and coverage is deemed acceptable, complete website integration and deploy.

Notes for future phases

- Phase 2: Expand extractors to Python and Script-Fu built-ins, add support for third-party plug-ins, and consider historical catalogs.
- Phase 3: Improve UI, search, and cross-linking to source code, and implement richer provenance queries.

Appendix: Useful references in this repository

- scripts/capture_pdb_poc.py — a proof-of-concept that queries a running GIMP's PDB using the Python batch interpreter.
- scripts/build_pdb.py — the existing Script-Fu and native C (app/pdb) source tokenizer and Script-Fu indexer.
- documentation/gimp-file-survey.md — survey of how procedures are registered across Script-Fu, Python, plug-in C, and native app/pdb files.

End of Phase 1 plan.
