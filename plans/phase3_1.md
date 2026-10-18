---
title: "Issue 3: C Plug-in Registration POC"
document_type: investigation-plan
version: "0.1.0"
status: draft
created: 2026-10-18
updated: 2026-10-18
issue: https://github.com/DoctorU/online-gimp-pdb-browser/issues/3
parent_plan: ../documentation/plan/phase1.md
---

# Issue 3: C Plug-in Registration POC

> **Status: Draft.** This is a bounded feasibility experiment under Phase 1,
> which remains in development. The POC does not implement the production
> catalog extractor or authorize publishing sample records as complete
> coverage.

## Purpose

Determine whether GIMP's built-in C plug-ins can be compiled and run in a
reduced collector environment that captures their registered procedure
metadata without requiring a normal, fully functioning GIMP installation.
Use `plug-ins/help/help.c` and `plug-ins/common/file-png.c` as contrasting
examples.

The result must distinguish:

1. Procedure names and metadata declared by source.
2. Procedures observed after GIMP's normal plug-in host loads them into a
   live PDB.
3. Procedure registrations observed directly by a collector while exercising
   the plug-in registration path.

Only the third result demonstrates the proposed registration-capture
approach. A successful live-PDB export is a useful baseline, not proof that a
reduced collector works.

## Experiment outline

### 1. Pin and isolate the GIMP source

1. Identify the stable GIMP 3 release and exact source revision relevant to
   the Phase 1 catalog. Record the tag, commit, and source URL in the POC
   results so subsequent comparisons use the same code.
2. Clone the official GIMP repository into the ignored `tmp/` directory, not
   into the application source tree. For example:

   ```sh
   git clone --filter=blob:none --no-checkout \
     https://gitlab.gnome.org/GNOME/gimp.git tmp/gimp-src
   git -C tmp/gimp-src fetch --depth 1 origin <release-tag-or-commit>
   git -C tmp/gimp-src checkout --detach FETCH_HEAD
   git -C tmp/gimp-src rev-parse HEAD
   ```

   Use the verified release tag or commit in place of the placeholder. If the
   upstream server does not support the partial-clone option, retry with a
   normal clone. Keep all generated build and install output under `tmp/`.
3. Inspect the two plug-ins' build definitions and registration entry points.
   Map which plug-in API calls create procedures and set their metadata, and
   what host/runtime calls occur before those procedures can be enumerated.
   Treat `app/pdb` native procedure registration as a separate family, not as
   the implementation of these plug-ins.

### 2. Establish a real GIMP build and runtime baseline

1. Install the build dependencies documented by the pinned GIMP revision.
   Record the host OS, compiler, Meson/Ninja versions, and relevant configure
   options. Do not introduce a custom CI container.
2. Configure a normal source build with a private install prefix under
   `tmp/`, then build and install it. For example:

   ```sh
   meson setup "$PWD/tmp/gimp-build" "$PWD/tmp/gimp-src" \
     --prefix="$PWD/tmp/gimp-install"
   meson compile -C "$PWD/tmp/gimp-build"
   meson install -C "$PWD/tmp/gimp-build"
   ```

   Keep the build directory and install prefix separate from the checked-out
   source. If dependencies are unavailable, record the configure failure and
   address only the prerequisites documented for this build.
3. Run the two plug-ins through the GIMP-provided headless/console runtime.
   Use the existing live-PDB capture POC as a control and record which target
   procedures appear, the metadata exposed, and any optional-dependency or
   plug-in-loading failures. First verify that the private install's console
   executable starts with its required runtime environment; then invoke the
   existing POC with `GIMP` pointing to that executable. A configured-out or
   unloadable example is recorded as unavailable in this baseline, not
   misreported as a successful capture.
4. Compare the result with each source's registration code. Label source
   declarations and live-PDB observations as such; do not describe either as
   collector-captured registrations.

This step intentionally builds a known-good reference first. It answers
whether the examples compile and run at the selected revision and supplies
expected metadata against which the reduced experiment can be checked.

### 3. Test whether the registration path can be reduced

Start with the smaller `help.c` example. Do not begin by replacing a large
part of GIMP or assuming that substituting `libgimp` is sufficient.

1. Follow the actual GIMP 3 plug-in lifecycle for the selected example:
   process startup, host negotiation, procedure discovery/creation, and
   transfer or registration of procedure metadata.
2. Identify the narrowest boundary at which real procedure metadata can be
   observed. Prefer reusing GIMP's real procedure and parameter types where
   practical, with a small collector at the host/registration boundary.
3. Build a reduced executable or shim around the actual plug-in registration
   code. Stub only the runtime services proven unnecessary by the dependency
   trace. Avoid mocking broad GIMP APIs before establishing which calls the
   plug-in actually requires.
4. Execute the plug-in registration path and serialize the resulting
   procedure metadata. Record every mocked or replaced API and any metadata
   that could not be preserved.
5. Only if the first example works, repeat with `file-png.c`. This is the
   harder case because its registration path and dependencies may include
   file-procedure and format-specific metadata or optional build
   dependencies.
6. If a proposed wrapper/interposition strategy is considered, demonstrate
   that it observes the real registration path for both examples. Do not
   assume dynamic symbol wrapping or replacement of `libgimp` works without
   testing; distinguish a link-time shim from the normal GIMP host.

If producing the reduced executable requires effectively rebuilding or
mocking most of GIMP's host/runtime, stop and document that finding instead of
expanding the mock without a bounded rationale. Compare its cost and fidelity
with running the normal headless GIMP build.

### 4. Validate the captured output

- Capture procedure name, procedure type, label/title, description/help,
  attribution, menu paths, arguments, return values, and file metadata where
  available.
- Check that the collector's output agrees with the real runtime baseline
  for the same source revision and plug-in configuration.
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

Proceed from the real-runtime baseline to the reduced collector only after
recording the actual plug-in lifecycle and required APIs. Proceed from
`help.c` to `file-png.c` only when the first example yields registrations
through the reduced path and its output can be validated.

At the end, report one of these conclusions with evidence:

- **Feasible:** both examples execute their registration path in the reduced
  collector, produce the required metadata, and pass the repeatable check.
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

1. A pinned source revision and reproducible build/run instructions.
2. A real-runtime baseline for `help.c` and `file-png.c`.
3. A reduced collector prototype if the dependency investigation supports one.
4. Example JSON output labelled with its evidence/capture method.
5. Focused validation and a repeatable smoke check.
6. A short findings summary documenting prerequisites, unsupported cases,
   feasibility decision, and implications for Phase 1.

## Out of scope

- Extracting all built-in C plug-in or native `app/pdb` procedures.
- Integrating the POC into `scripts/build_pdb.py` or the production catalog.
- Publishing the POC's example output as complete coverage.
- Designing the final catalog schema or browser experience.
- Building a bespoke container image or production CI workflow.

## Related references

- [Issue #3: POC — extract plug-in C procedures](https://github.com/DoctorU/online-gimp-pdb-browser/issues/3)
- [Phase 1 outcome baseline](../documentation/plan/phase1.md)
- [Live PDB metadata-export POC](../documentation/procedure-extraction-poc.md)
- [Project work tracker](../TODO.md)
