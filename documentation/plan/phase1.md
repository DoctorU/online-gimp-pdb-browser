---
title: "Phase 1: Built-in C Procedure Coverage"
document_type: phase-baseline
version: "0.4.0"
status: in development
created: 2026-10-18
updated: 2026-10-18
parent_plan: ./program.md
work_tracker: ../../TODO.md
---

# Phase 1: Built-in C Procedure Coverage

> **Status: In development.** This is the current reference for Phase 1, and
> will be kept accurate as POCs, evidence, and implementation evolve. Phase 1
> is not complete until the completion criteria below are met.

## Outcome

Phase 1 establishes the online browser as a dependable reference for the
built-in C procedures available in the standard Linux GIMP 3 environment.
The catalog contains both native `app/pdb` procedures and procedures
registered by built-in C plug-ins, alongside the existing Script-Fu entries.

GIMP developers and plug-in authors can find a procedure and understand its
purpose, inputs, outputs, and other available registration metadata from a
browser without installing or running GIMP locally.

## User-facing baseline

The Phase 1 catalog:

- Covers the agreed native C and built-in C plug-in procedure families, as
  exposed by the documented standard Linux environment.
- Preserves the existing Script-Fu catalog and native `gimp-*` records.
- Presents procedure identity, descriptions, arguments, return values, menu
  locations, attribution, file-format properties, and source links where
  those fields are available.
- Identifies the GIMP release and exact source revision represented.
- Makes the catalog's coverage boundary and known omissions clear.
- Is generated and published through a repeatable process; an invalid or
  incomplete update does not replace the last known-good publication.

## Scope

Included:

- Native C procedures registered in GIMP's `app/pdb`.
- Built-in C plug-in procedures.
- The existing built-in Script-Fu catalog.
- Browser presentation, metadata normalization, provenance, validation, and
  publication needed to make the combined catalog useful and trustworthy.

Not included:

- Third-party plug-ins installed by individual users.
- Procedures unavailable in the standard Linux environment because of
  optional dependencies, unless explicitly included in a documented coverage
  extension.
- Python plug-in extraction, which is a later program phase.
- Historical catalog browsing; the reference represents the latest stable
  GIMP 3 release.

## Coverage and trust

Catalog entries may be produced by different extraction methods. The
published result distinguishes procedure families and records provenance;
source parsing, live-PDB observation, and registration-call capture are not
treated as equivalent evidence.

The capture approach and metadata contract are implementation details tracked
in the work tracker and related issues. This plan is updated when POCs or
findings change what is known about the outcome, scope, coverage, or
limitations. Regardless of method, Phase 1 coverage is not considered complete
based on representative examples alone: publication requires an agreed,
measurable baseline and passing validation for both in-scope C families.
Conditional registrations and unsupported patterns are reported rather than
silently presented as covered.

Scope may be refined while Phase 1 is in development. Newly agreed Phase 1
requirements are recorded here. Any functionality explicitly deferred from
Phase 1 is recorded in a separate `documentation/plan/phase2.md` with status
`draft`, along with an explicit note that Phase 1 remains in development. A
Phase 2 draft does not change Phase 1's status or completion criteria.

## Phase 1 completion criteria

Phase 1 is complete when:

1. The latest stable GIMP 3 catalog includes the agreed, validated coverage
   for native `app/pdb` C and built-in C plug-in procedures, while preserving
   existing Script-Fu entries.
2. Users can search and browse these records online without running GIMP.
3. Records link to the correct GIMP source revision and expose available
   metadata in a consistent way.
4. A repeatable automated pipeline checks provenance, catalog structure, and
   the agreed coverage threshold before publication.
5. Failed validation leaves the last known-good site in place.
6. The setup, coverage boundary, limitations, and update process are
   documented.

## Related work

Execution status and remaining tasks are maintained in the
[Phase 1 work tracker](../../TODO.md), not in this outcome baseline. The current
issue map is:

- [Parent issue #1: Add additional missing PDB procedures](https://github.com/DoctorU/online-gimp-pdb-browser/issues/1)
- [Issue #2: Survey GIMP procedure registration patterns (completed)](https://github.com/DoctorU/online-gimp-pdb-browser/issues/2)
- [Issue #3: POC — extract plug-in C procedures](https://github.com/DoctorU/online-gimp-pdb-browser/issues/3)
- [Issue #4: Modularize the catalog builder](https://github.com/DoctorU/online-gimp-pdb-browser/issues/4)
- [Issue #5: Design procedure browser navigation](https://github.com/DoctorU/online-gimp-pdb-browser/issues/5)

## Version history

| Version | Date       | Status | Summary | Reason |
|---------|------------|--------|---------|--------|
| 0.1.0   | 2026-10-18 | Approved | Initial Phase 1 scope | Define C extraction and browser integration goals. |
| 0.2.0   | 2026-10-18 | Review | Added remaining-work sequence and issue alignment | Translate the scope into sequenced execution work. |
| 0.3.0   | 2026-10-18 | Review | Reframed as completed-state user baseline; moved execution tracking to `TODO.md` | Keep the phase reference outcome-focused and separate it from task status. |
| 0.4.0   | 2026-10-18 | In development | Marked as a living reference while POCs and findings evolve; defined how deferred scope moves to a Phase 2 draft | Keep the plan accurate during implementation and make clear that Phase 1 remains active. |
