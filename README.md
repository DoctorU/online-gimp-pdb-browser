# GIMP Procedure Browser — Project Overview

This repository provides a browsable, versioned online reference for GIMP's Procedure Database (PDB) aimed at GIMP
extension authors and GIMP developers. The site lets users discover procedures, inspect their parameters and
metadata, and jump to source where available.

This project began as a Script-Fu index, but the long-term goal is broader: include native `app/pdb` C procedures,
C-based plug-in procedures, and built-in Python and Script-Fu procedures. Phase 1 focuses on extracting C-registered
procedures and integrating them into the website; later phases will expand coverage and polish.

Key points

- Audience: GIMP developers and plug-in authors who need an authoritative reference for callable procedures.
- Phase 1 goal: Prototype and validate a collector for C-registered procedures (native `app/pdb` and built-in plug-ins),
  normalize the observed metadata, and integrate the generated catalog into the website for the latest stable GIMP 3 release.
- Scope for Phase 1: Linux/Ubuntu CI and Linux local setup (broader OS support later).
- Release policy: The site publishes the latest stable GIMP 3 catalog only when extraction and validation succeed; failed runs keep the last-known-good live catalog.

What is Phase 1 intended to deliver?

- Documented local development and build instructions for the prototype collector and environment.
- A repeatable extraction command/script that produces a versioned JSON catalog.
- A validated JSON catalog produced in CI and published as the live site only after validation passes.
- Integration of C procedures into the browser UI (the site will be updated to display the new C catalog fields).
- A coverage report and a documented list of limitations (environment-dependent or conditional procedures that were not observed in the standard Linux runtime).

Extraction approach (experimental)

Phase 1 will prototype a lightweight collector that intercepts or captures procedure registrations. Because native `app/pdb`
registrations happen inside GIMP while plug-in C registrations happen through the plug-in host, the prototype will:

- Implement and test one representative example capture for each family (native `app/pdb` and built-in C plug-ins) using a stub/collector approach.
- Use the evidence from the prototypes to choose a robust capture architecture for full coverage.

If necessary for validation, Phase 1 may investigate running a full GIMP build in CI as an oracle to compare against the lightweight collector; this is a feasibility question to be answered by the prototype.

Automation and CI

- The canonical workflow checks upstream for the latest stable GIMP 3 revision daily. If the stable revision changed, the workflow will run the extraction and validation pipeline. Only successful validated runs will replace the live catalog.
- CI target platform for Phase 1: Ubuntu (ubuntu-latest) to keep the runtime predictable.
- If extraction validation fails, the workflow should fail and preserve the previous live site.

Metadata and normalization

The collector will record all safely observable registration metadata (procedure identifier, title/label, description/blurb, help, help id, author/copyright/date, menu paths, image/drawable types, arguments, return values, and file-format metadata for load/export procedures).

The website will normalize collected records into the existing JSON catalog format used by the static site and show fields that make sense in the UI.

Acceptance criteria for Phase 1

- A repeatable extraction that runs locally on a documented Ubuntu development environment and produces a stable JSON output for an identified GIMP stable revision.
- CI job capable of running the extractor and validating the produced JSON against schema and coverage checks.
- Integration work to permit the browser to display the new C-procedure fields without degrading the existing Script-Fu information.
- A coverage report that documents gaps and environment-dependent procedures.

Open risks and unknowns

- A single lightweight stub may not capture both native `app/pdb` registrations and plug-in C registrations. The prototype will determine whether separate capture mechanisms are required.
- Some plug-ins advertise procedures conditionally (depending on external dependencies); the Phase 1 catalog will only claim coverage for procedures observed in the standard Linux CI/runtime environment.
- CI cost/complexity if a full GIMP build is required for validation. The plan assumes local runs are available if CI proves too expensive; the prototype will measure feasibility.

Next steps (Phase 1)

- Prototype a minimal libgimp stub/collector for a built-in C plug-in and a representative native `app/pdb` procedure capture.
- Produce a coverage/validation checklist and schema for the JSON catalog.
- Update the website data model and UI to accept and render the new C fields (source links, parameter lists, file-format metadata).
- Implement CI jobs that run extraction, validate outputs, and publish the site only on successful validation.

Developer resources

- See documentation/procedure-extraction-poc.md for an existing live-PDB capture proof-of-concept (queries a running GIMP).
- See documentation/gimp-file-survey.md for the registration patterns encountered in GIMP source (native vs plug-in vs Script-Fu/Python considerations).

License

This project follows GPL-3.0-or-later (matching GIMP's license). See LICENSE for details.