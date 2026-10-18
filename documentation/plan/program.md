---
title: GIMP Procedure Browser — Program Goals and Roadmap
document_type: program-plan
version: "1.0"
status: approved
created: 2026-10-18
updated: 2026-10-18
---

# GIMP Procedure Browser: Program Goals and Roadmap

## Program purpose

The GIMP Procedure Browser aims to be a dependable, browsable online reference
for GIMP developers and plug-in authors who need to discover and understand
procedures callable through GIMP's Procedure Database (PDB).

The central outcome is a catalog that helps users answer:

- What procedures does this GIMP release provide?
- What does a procedure do, and what arguments and return values does it have?
- Where is it available in GIMP's menus, if anywhere?
- What source implementation and GIMP revision correspond to this entry?

The project is not intended to replace GIMP's in-application Procedure Browser
or documentation. It is an online companion optimized for discovery, browsing,
and linking procedure information to its source. Users should be able to keep
the reference open in a web browser and look up procedures without installing
or running GIMP locally.

## Long-term goals

1. **Broad built-in procedure coverage.** Catalog native procedures
   implemented under `app/pdb`, built-in C plug-in procedures, and built-in
   Python and Script-Fu procedures.
2. **Useful metadata.** Preserve all reliably available procedure metadata,
   including identity, descriptions, help, attribution, arguments, return
   values, menu paths, relevant file-format properties, and source locations.
3. **Trustworthy provenance.** Identify the exact GIMP version and source
   revision represented by each generated catalog, and make coverage limits
   visible rather than implying unsupported completeness.
4. **A stable online reference.** Keep the site current with the latest stable
   GIMP 3 release. A failed or invalid catalog update must not replace the last
   known-good published site.
5. **Repeatable maintenance.** Make catalog generation and validation
   reproducible, automated where practical, and documented for local
   development.

## Audience

The primary audience is GIMP developers and plug-in authors. The catalog
should be understandable to people who need to call, implement, or debug
procedures, without requiring them to search through GIMP source first.

## Program boundaries

### Included

- Built-in procedures shipped with GIMP: native `app/pdb` procedures, C
  plug-ins, Python plug-ins, and Script-Fu.
- A static, browsable site backed by generated catalog data.
- A user-facing reference that does not require GIMP to be installed or
  running on the visitor's computer.
- Procedure metadata and source links, with the catalog tied to a specific
  stable GIMP revision.
- Extraction and validation tooling, plus documentation of coverage and
  known gaps.

### Not currently included

- Cataloging third-party plug-ins installed by individual users.
- Historical catalog browsing or maintaining a selectable archive of old
  GIMP releases. The initial policy is to publish the latest stable catalog
  only.
- Reproducing all runtime behavior of GIMP or invoking procedures from the
  website.
- Claiming every theoretically possible procedure is present when its
  registration depends on optional components or runtime environment.

These boundaries can be reconsidered in future phases if user needs or
technical evidence justify changing them.

## Product principles

- **Describe the real source and scope.** Distinguish procedures found in
  source from procedures observed in a particular runtime environment.
- **Prefer behavioral evidence where useful.** Static declarations, runtime
  PDB queries, and registration interception answer different questions; do
  not treat them as interchangeable without validation.
- **Keep uncertainty explicit.** Document unsupported patterns, conditional
  registrations, missing fields, and environment assumptions.
- **Preserve provenance.** Generated data should carry the GIMP release and
  exact revision used, with source links anchored to that revision.
- **Protect the published reference.** Validate changes before deployment and
  retain the last known-good site if an update fails.
- **Normalize without erasing distinctions.** Different procedure families
  can share a browsable schema while retaining their source kind, metadata
  differences, and family-specific fields.
- **Separate extraction from presentation.** The catalog-generation pipeline
  should be testable independently from the static website UI.

## Roadmap

The phases below are a planning structure, not a promise of fixed dates or
implementation choices. Each phase should build on the catalog and
documentation produced by earlier work. Scope can be refined based on
prototype evidence.

### Phase 1: C procedure extraction and initial integration

Establish a Linux/Ubuntu development and CI path for native C procedures and
built-in C plug-ins. Prototype a lightweight registration collector against
representative examples from both families, determine whether their capture
mechanisms can be shared, and document the coverage and limitations.

After the extraction and validation approach is sufficiently reliable, emit a
versioned JSON catalog, integrate the C entries into the browser, and deploy
the latest stable GIMP 3 catalog. Prototype samples alone are not a production
catalog and must not be published as complete coverage.

The Phase 1 plan is in [phase1.md](./phase1.md).

### Phase 2: Python and Script-Fu coverage

Add built-in Python and Script-Fu procedure families to the catalog, either by
extending existing extraction tools or by introducing family-appropriate
extractors. Preserve shared catalog and provenance conventions, and document
any remaining coverage gaps.

The exact extraction strategy, order, and acceptance criteria for this phase
remain to be defined after Phase 1.

### Future extensions

Potential extensions include improved search and filtering, richer
cross-references, broader platform support, historical release catalogs, or
third-party plug-in catalogs. These are possibilities, not current
commitments; each should have its own scope and acceptance criteria before
work begins.

## Program-level success measures

The program is succeeding when:

- Users can browse the agreed built-in procedure families for the current
  stable release.
- Visitors can search and read the published catalog in a browser without
  installing or running GIMP locally.
- Entries expose useful, consistently structured metadata and source links
  where available.
- The catalog clearly states its GIMP version, revision, and coverage
  limitations.
- Catalog generation and validation can be repeated without relying on
  undocumented manual steps.
- Failed upstream updates do not silently replace the last known-good
  publication.

## Open program questions

The following are technical questions to resolve through the phases, not
assumptions already proven:

- Can C plug-ins be run against a minimal `libgimp` stub in a collector, and
  what subset of GIMP APIs would that require?
- Can native `app/pdb` registrations be captured by a similarly lightweight
  method, or do they require a different harness or a normal GIMP build?
- How closely can collected registration metadata be compared with the live
  PDB, and what should count as sufficient coverage for publication?
- Which procedure registrations are absent in the standard Ubuntu
  environment because of optional external dependencies?
- Is building and running full GIMP in CI practical, or should it be used
  only for local validation?
- What stable-release signal should trigger a catalog update, and how should
  failures be reported and retried?

The existing [live PDB capture proof of concept](../procedure-extraction-poc.md)
queries the PDB after GIMP loads its procedures. It can help investigate
runtime-visible metadata, but it does not intercept C registration calls or
establish that a lightweight collector is feasible.

## Version history

| Version | Date       | Status   | Summary                                  | Reason                                      |
|---------|------------|----------|------------------------------------------|---------------------------------------------|
| 1.0     | 2026-10-18 | Approved | Initial approved program goals and scope | Establish the project's agreed direction.  |
