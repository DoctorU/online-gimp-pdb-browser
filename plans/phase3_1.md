---
title: "Issue 3: C Plug-in Registration POC"
document_type: investigation-plan
version: "0.3.0"
status: approved for poc
created: 2026-10-18
updated: 2026-10-18
issue: https://github.com/DoctorU/online-gimp-pdb-browser/issues/3
parent_plan: ../documentation/plan/phase1.md
---

# Issue 3: C Plug-in Registration POC

> **Status: Approved for POC.** This is a bounded feasibility experiment
> under Phase 1, which remains in development. The POC does not implement the
> production catalog extractor or authorize publishing sample records as
> complete coverage.

## Purpose

Determine whether the actual GIMP 3 built-in C plug-in procedure-construction
path can be exercised by a collector, and whether this can be done without
GIMP's normal plug-in host/runtime. Use `plug-ins/help/help.c` and
`plug-ins/common/file-png.c` as contrasting examples. Feasibility is an
explicit investigation result, not an assumption or a prerequisite already
settled by the plan.

The result must distinguish:

1. Procedure names and metadata declared by source.
2. Procedures observed after GIMP's normal plug-in host loads them into a
   live PDB.
3. Procedure metadata returned by a harness that exercises the plug-in's
   actual `query_procedures()` and `create_procedure()` callbacks.
4. Procedures observed after GIMP's normal plug-in host registers the
   plug-in-created procedures in the live PDB.

Callback output demonstrates that the plug-in code created the metadata; it
does not by itself demonstrate registration with GIMP's PDB. Only live-host
observation demonstrates the latter. Keep both evidence types distinct.

## Experiment outline

### 1. Pin and isolate the GIMP source

1. Select a stable GIMP 3 release relevant to Phase 1 and record its tag and
   resolved commit SHA. The upstream source is an input to this POC; no
   changes will be pushed to the GIMP repository.
2. Clone GNOME's read-only GitHub mirror,
   [`GNOME/gimp`](https://github.com/GNOME/gimp), at the selected release tag
   into ignored `tmp/`. Pinning and recording the resolved commit makes the
   investigation reproducible; write access to the upstream repository is
   not needed.

   ```sh
   GIMP_REF='<verified-release-tag>'
   git clone --depth 1 --branch "$GIMP_REF" \
     https://github.com/GNOME/gimp.git tmp/gimp-src
   git -C tmp/gimp-src rev-parse HEAD
   ```

   Replace the placeholder with the selected release tag. Keep all generated
   build and install output under `tmp/`.
3. Before compiling, inspect the pinned revision's `GimpPlugIn` lifecycle,
   both examples' `query_procedures()` and `create_procedure()` callbacks,
   their Meson target definitions, and the plug-in host's query/registration
   protocol. Map the APIs used to construct each procedure and identify which
   require a live GIMP host, UI, or external libraries. `app/pdb`'s native
   registration path is a different subsystem and is not a proxy for the
   plug-in path.
4. Write a short feasibility assessment from this source trace: what can be
   invoked directly, what requires the host/protocol, what can be stubbed
   without changing procedure construction, and what remains uncertain.
   Choose the first example based on the traced build/runtime dependencies;
   do not assume `help.c` is simpler.

This source-level investigation is part of the POC: the current inspection of
upstream `master` is useful orientation, but it does not establish feasibility
for the pinned stable release.

### 2. Establish the runtime baseline and decide whether a source build is needed

After the source review, check whether an already available GIMP 3 runtime
(including the user's Flatpak installation) can supply the live-PDB comparison
for the selected examples. Record its GIMP version, available plug-ins, and
capture method. This result is a runtime baseline, not evidence of reduced
collection.

Build GIMP from source only if the available runtime cannot answer the
question, or a runtime matching the pinned source revision is needed. Meson
is the build system, not a special Linux image: a future GitHub Actions job
could use a GitHub-hosted Ubuntu runner, install the pinned revision's
documented build dependencies and Meson/Ninja, then configure and build. Do
not create a custom container image for this POC. Establish the dependency set
and build cost locally before proposing CI.

For a source build, record the host OS, compiler, Meson/Ninja versions, and
options. Check the pinned `meson_options.txt` and dependency report before
building. `enable-console-bin=true` produces a console-only executable, but
does not remove GIMP's runtime or plug-in host. Keep the build directory and
private install prefix under ignored `tmp/`. For example:

   ```sh
   meson setup "$PWD/tmp/gimp-build" "$PWD/tmp/gimp-src" \
     --prefix="$PWD/tmp/gimp-install" \
     -Denable-console-bin=true
   meson configure "$PWD/tmp/gimp-build"
   ```

Run compile and install only if the configured build is needed and its
dependency report is acceptable:

   ```sh
   meson compile -C "$PWD/tmp/gimp-build"
   meson install -C "$PWD/tmp/gimp-build"
   ```

If dependencies are unavailable or build cost is unreasonable, record the
exact blocker rather than silently downgrading the required evidence. A
configured-out or unloadable example is unavailable for the runtime baseline,
not a successful capture and not evidence that its source has no registration.

### 3. Test the narrowest viable collection boundary

Use the source assessment to pick one example and begin at the narrowest
boundary that retains the real procedure-construction callbacks. Do not begin
by replacing a large part of GIMP or assuming that substituting `libgimp` is
sufficient.

1. First test whether the compiled plug-in can be run in its normal query mode
   or whether its actual callback path can be invoked with GIMP's real
   `GimpProcedure` types outside the host. Record exactly which lifecycle
   callbacks ran.
2. Serialize procedure objects returned from the real `create_procedure()`
   callback. A harness that invokes this callback captures plug-in-produced
   metadata; it must not claim that the procedure was registered with the
   main GIMP PDB unless the host's registration step also ran.
3. If direct invocation is not viable, inspect and test the actual plug-in
   protocol boundary. Consider a small host-side observer or running the
   normal GIMP host. Any stub, wrapper, or interposition must preserve the
   callback and procedure-construction behavior, and its limits must be
   recorded.
4. Only after one example works, repeat the approach with the other example.
   Verify build dependencies (including optional ones) rather than assuming
   either plug-in is simpler.
5. Do not use `gimp_pdb_register_procedure()` interception as evidence for
   these plug-ins unless the pinned source trace proves that it is on their
   registration path. Do not use source-text parsing as a substitute for
   executing the procedure-construction code.

If producing a reduced executable requires effectively rebuilding or
mocking most of GIMP's host/runtime, stop and document that finding instead of
expanding the mock without a bounded rationale. Compare its cost and fidelity
with using the normal headless GIMP host.

### 4. Validate captured output

- Capture procedure name, procedure type, label/title, description/help,
  attribution, menu paths, arguments, return values, and file metadata where
  available.
- Compare callback-harness and live-host output for the same source revision
  and plug-in configuration. Account for metadata normalized or supplied by
  the host and control locale where practical.
- Preserve provenance for source revision, build options, example plug-in,
  and capture method.
- Add focused tests for serialization and a repeatable smoke command that
  fails explicitly if the capture is empty or a procedure expected from a
  successfully built and loaded example is missing. Report an example that
  was not built or could not load as unavailable with its reason; it cannot
  count as evidence that the reduced collector works.
- Keep the artifact and command confined to the POC. Do not write sample
  records into production `data/pdb.json`.

## Decision gates

Proceed to a build or reduced harness only after the pinned-source assessment
explains why it is needed and identifies the boundary to test. Proceed to the
second example only when the first demonstrates a repeatable, correctly
labelled capture.

At the end, report one of these conclusions with evidence:

- **Feasible:** both examples' actual procedure-construction callbacks run
  in the proposed collector, produce the required metadata, and pass the
  repeatable check; any claim of host registration is separately validated.
- **Feasible with limits:** identify the precise unsupported patterns,
  dependencies, and missing metadata, and explain why those limits do not
  invalidate the POC.
- **Not feasible as a lightweight collector:** identify the GIMP host/runtime
  services that could not be removed and recommend whether the normal
  headless runtime is the practical extraction route.

A failure to reproduce a procedure in the live PDB is not by itself proof
that its source lacks a registration, and source declarations alone are not
proof that the collector executed it.

## Deliverables

1. A pinned source revision and source-level lifecycle/build feasibility
   assessment.
2. A runtime baseline for `help.c` and `file-png.c`, using an available GIMP
   runtime or a documented source build when necessary.
3. A reduced collector prototype if the assessment supports one.
4. Example JSON output labelled with its evidence/capture method.
5. Focused validation and a repeatable smoke check.
6. A short findings summary documenting prerequisites, unsupported cases,
   build/CI implications, feasibility decision, and implications for Phase 1.

## Out of scope

- Extracting all built-in C plug-in or native `app/pdb` procedures.
- Integrating the POC into `scripts/build_pdb.py` or the production catalog.
- Publishing the POC's example output as complete coverage.
- Designing the final catalog schema or browser experience.
- Implementing a production CI workflow. The POC may estimate feasibility on
  a GitHub-hosted Ubuntu runner but does not need a custom container image.

## Related references

- [Issue #3: POC — extract plug-in C procedures](https://github.com/DoctorU/online-gimp-pdb-browser/issues/3)
- [Phase 1 outcome baseline](../documentation/plan/phase1.md)
- [Live PDB metadata-export POC](../documentation/procedure-extraction-poc.md)
- [Project work tracker](../TODO.md)

## Plan history

| Version | Date       | Summary | Reason |
|---------|------------|---------|--------|
| 0.2.0   | 2026-10-18 | Added a pinned-source feasibility gate, distinguished plug-in callback metadata from host registration, made source builds conditional, and documented the GitHub mirror and future Ubuntu-runner option | Address the GIMP lifecycle and build-model uncertainties before starting an expensive build or collector implementation. |
| 0.3.0   | 2026-10-18 | Approved the plan for the full POC and clarified that source review is the first step, not the limit of the work | Authorize the bounded investigation and capture experiment while keeping source builds conditional on need. |
