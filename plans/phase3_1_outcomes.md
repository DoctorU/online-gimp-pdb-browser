---
title: "Issue 3 POC Outcomes"
document_type: investigation-log
version: "0.4.0"
status: in progress
created: 2026-10-19
updated: 2026-10-19
plan: ./phase3_1.md
issue: https://github.com/DoctorU/online-gimp-pdb-browser/issues/3
---

# Issue 3 POC Outcomes

This file records evidence and conclusions as work proceeds under the
[Issue 3 POC plan](./phase3_1.md). It distinguishes source inspection,
runtime observations, and collector experiments. A source-level indication
of feasibility is not recorded as a successful execution result.

## 2026-10-19 — Source pin and initial source review

### Source revision

- Selected stable release: **GIMP 3.2.6**. The release tag's source README
  identifies it as a stable release in the GIMP 3.2 series, and `meson.build`
  declares version `3.2.6`.
- Repository: [`GNOME/gimp`](https://github.com/GNOME/gimp), the read-only
  GitHub mirror. The source is used as an input to this investigation; no
  upstream changes are planned.
- Release tag: `GIMP_3_2_6`.
- Annotated tag object: `2836b29d1291cd62513a26da87e744914e29fd61`.
- Resolved commit: `e101dd19b165f927d3ba0a74658a71537c5661b9` (`Release GIMP
  3.2.6!`, 2026-09-10).
- Canonical local checkout: `tmp/gimp-src`, now detached at the resolved
  commit. Its earlier detached `master` checkout (`eff4619...`) was replaced
  after the user confirmed this is the canonical clone and approved updating
  it.
- The repository's existing `build/` source directory was preserved. It
  contains GIMP's platform build scripts; no configured Meson build directory
  has been identified or reused.
- A temporary duplicate clone was created while initially treating
  `tmp/gimp-src` as unrelated. After clarification, the canonical checkout was
  pinned and the duplicate was removed; all source inspection now uses
  `tmp/gimp-src`.

### Plug-in lifecycle and registration boundary

Inspection of the pinned `libgimp/gimpplugin.c` shows the plug-in-side
lifecycle:

1. GIMP's plug-in base class supports query, init, and run modes.
2. In query mode, the plug-in's `query_procedures()` callback returns names.
   The framework passes each name to `create_procedure()`.
3. The returned `GimpProcedure` is installed by the plug-in-side framework.
   `gimp_procedure_real_install()` serializes procedure and parameter
   definitions over the plug-in wire channel. GIMP's application-side
   plug-in manager handles the `GP_PROC_INSTALL` message and adds the
   corresponding host-side procedure.
4. The application launches the plug-in in query mode and reads its wire
   messages. Thus, the `app/pdb` native `gimp_pdb_register_procedure()` path
   is not the registration boundary for these plug-ins.

The install step also makes separate PDB calls for metadata such as image
types, menu labels and paths, documentation, attribution, and file-procedure
properties. Therefore, intercepting only the `GP_PROC_INSTALL` message would
not capture the full metadata used by these examples. These metadata calls go
through `_gimp_pdb_run_procedure_array()`: it writes a `GP_PROC_RUN` message
and waits for a `GP_PROC_RETURN` before continuing. A protocol-level collector
would have to handle those calls and reply, not only read install messages.
The source objects have getters for much of this metadata, so serializing a
procedure object returned by `create_procedure()` before installation may
avoid implementing those host RPCs; this remains an approach to test, not a
verified result.

`GimpProcedure` construction itself creates a local GObject and stores
metadata. However, a `GimpPlugIn` object is not simply ready for construction
with `g_object_new()`: its `constructed` method asserts that read and write
channels are present and initializes the plug-in wire protocol. The normal
`gimp_main()` path obtains those channels from file descriptors, initializes
GIMP types and locale state, and then instantiates the plug-in subclass.
The normal framework also calls the plug-in's i18n setup before
`create_procedure()`; a direct callback harness would need to preserve that
ordering for localized procedure fields.

This suggests a useful distinction for the experiment: invoking the real
procedure-construction callbacks and inspecting returned objects may be
possible without installing them in the host PDB, but reproducing normal
query/installation behavior requires satisfying the plug-in initialization
and wire-protocol boundary. A standalone callback harness has **not** been
built or tested, so its feasibility remains open.

### Example procedures and build definitions

- `plug-ins/help/help.c` registers `extension-gimp-help` from its query
  callback. Its callback creates a persistent procedure with attribution and
  two string-array arguments. It also creates a temporary procedure during
  execution of the persistent procedure; that runtime-added procedure is not
  part of the ordinary query result and must not be conflated with it.
- The Help plug-in's Meson target compiles several help support sources into
  a static library and uses `libgimpui`, GIO, and GDK Pixbuf. Although its
  main procedure's metadata shape is relatively simple, the target does not
  consist only of `help.c`.
- `plug-ins/common/file-png.c` declares three query names: `file-png-load`,
  `file-apng-load`, and `file-png-export`. Its creation callbacks build
  load/export procedure types and attach file-format metadata; the export
  procedure adds further typed arguments and capabilities.
- The `file-png` Meson entry lists libpng and lcms as plug-in dependencies.
  The common plug-in build rule also links GIMP libraries, including
  `libgimpui`. Neither example can yet be assumed to be the simpler
  standalone build target; the Help plug-in brings its own support sources
  and UI dependencies.
- In both examples, the callbacks are static functions wired into a
  `GimpPlugIn` subclass and entered through `GIMP_MAIN`.

### Local execution environment

In this workspace, `gimp-console-3.0`, `gimp-3.0`, Meson, Ninja, and the
`gimp-3.0` pkg-config package are unavailable. A C compiler, GLib/GObject/GIO,
and libpng are available; GTK 3, babl, GEGL, and lcms2 development packages
are unavailable. No GIMP build or runtime test has been attempted here. The
user's Flatpak runtime is not directly available to this workspace; its
version and capture output can be used as a separately labelled runtime
observation if provided.

## Preliminary assessment

The source confirms that plug-in procedure construction and host PDB
registration are separate stages. It also exposes a concrete constraint for
a lightweight harness: plug-in object initialization expects protocol
channels, and normal installation sends metadata to the host. Capturing the
returned `GimpProcedure` before installation may avoid implementing the host
PDB, but how to instantiate and run the real plug-in callbacks faithfully
without the normal entry path is not yet established.

No feasibility verdict is made yet. No collector, source build, live-PDB
export, or production catalog change has been made.

## 2026-10-19 — Registration interception and startup behavior

### What the `GP_PROC_*` messages mean

`GP_PROC_INSTALL`, `GP_PROC_RUN`, and `GP_PROC_RETURN` are wire-protocol
message types, not procedures that the collector would call as ordinary
functions. During plug-in query, `gimp_procedure_real_install()` sends
`GP_PROC_INSTALL` with the procedure name, type, arguments, and return values.
It then makes PDB calls for additional metadata; those calls travel as
`GP_PROC_RUN` messages, and the plug-in waits for the host's `GP_PROC_RETURN`.
Thus a protocol-only collector must execute the real plug-in query lifecycle,
receive the install message, and service the metadata RPCs. A normal GIMP host
does this already. A direct callback/object experiment that stops before
installation need not implement this protocol exchange.

### What headers and a shim would provide

GIMP headers declare the API and types that plug-in source code can call; they
do not contain the plug-in-specific procedure names or metadata, which are
created by the plug-in's compiled `query_procedures()` and
`create_procedure()` callbacks. A library made only from headers therefore
cannot extract those registrations.

A shim remains a possible experiment: compile the real plug-in source and
callbacks against GIMP-compatible API declarations plus replacement
implementations for the runtime behavior they use, then observe the resulting
procedure objects. To be meaningful, it must preserve the real callbacks and
enough of GIMP's object construction, type, lifecycle, and localization
behavior to avoid changing the metadata being captured. Alternatively, using
the real `libgimp` means satisfying its plug-in initialization and protocol
requirements; a protocol host would then need to service the install-time
metadata calls. Source review has not established how small a shim could be,
whether the selected plug-ins can be built against one without source
modifications, or whether that is less work than a normal headless GIMP host.
These are open experiment questions, not demonstrated feasibility.

### `gimp_pdb_register_procedure()` is on the plug-in host path

The application-side plug-in manager handles `GP_PROC_INSTALL`, constructs a
`GimpPlugInProcedure`, and stores it on the plug-in definition. During
`gimp_plug_in_manager_restore()`, the manager iterates these plug-in
procedures and `gimp_plug_in_manager_add_to_db()` calls
`gimp_pdb_register_procedure()` on each one. Therefore interception at that
application boundary **can** provide evidence of procedures actually
registered in the live host PDB, including plug-in procedures.

That is a valid host-backed capture approach, not evidence that a lightweight
standalone collector can work without the GIMP host. It must also distinguish
plug-in procedures from native PDB procedures (and temporary procedures),
retain useful provenance, and account for the runtime-dependent registrations
described below. The POC plan's current wording against treating
`gimp_pdb_register_procedure()` interception as evidence is too broad in light
of this trace; the plan remains unchanged pending review.

### What runs during startup

The `GimpPlugInClass` documentation says `query_procedures()` is normally
queried only after installation or update, while `init_procedures()` runs at
every startup and is intended for procedures that depend on runtime
conditions. The host restores cached plug-in query data, queries plug-ins
marked new/changed (or all plug-ins when `query_all` is enabled), then runs
initialization for plug-ins that advertise an init callback. It subsequently
starts persistent procedures with zero arguments as extensions.

This does **not** mean every plug-in procedure's actual operation runs at
startup. Most procedures are only executed when requested. But registration
is not universally a build-time constant: query and create callbacks execute
at runtime, initialization procedures explicitly support runtime-dependent
availability, and automatically started extensions do execute at startup.
For a representative catalog, the capture configuration and startup phase
must therefore be stated; one startup's PDB is a runtime observation, not
proof that every conditional procedure across all environments was captured.

## Next investigation steps

1. Trace which fields the existing live-PDB capture can retrieve and compare
   them to the fields available from each local `GimpProcedure` and
   `GimpFileProcedure` object.
2. Compare the possible evidence paths: intercept host registration to capture
   the PDB after normal loading, or test a host-independent collector using
   real callbacks and either a protocol host or a shim. The former is valid
   live-host evidence; it does not establish the latter's feasibility.
   Preserve plug-in initialization and i18n behavior in any host-independent
   test. Neither path is yet verified by execution in this workspace.
3. Check whether the user's existing Flatpak can provide the live-runtime
   baseline for the target procedures and record its exact version. If the
   source-matched build or selected harness requires a source build, explain
   why and assess dependencies first; this workspace currently lacks several
   required development packages and Meson/Ninja.

## Source references

- [`libgimp/gimpplugin.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/libgimp/gimpplugin.c)
- [`libgimp/gimp.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/libgimp/gimp.c)
- [`libgimp/gimpprocedure.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/libgimp/gimpprocedure.c)
- [`app/plug-in/gimppluginmanager-call.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/app/plug-in/gimppluginmanager-call.c)
- [`app/plug-in/gimppluginmanager-restore.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/app/plug-in/gimppluginmanager-restore.c)
- [`libgimp/gimpplugin.h` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/libgimp/gimpplugin.h)
- [`app/plug-in/gimpplugin-message.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/app/plug-in/gimpplugin-message.c)
- [`plug-ins/help/help.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/plug-ins/help/help.c)
- [`plug-ins/help/meson.build` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/plug-ins/help/meson.build)
- [`plug-ins/common/file-png.c` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/plug-ins/common/file-png.c)
- [`plug-ins/common/meson.build` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/plug-ins/common/meson.build)
- [`meson_options.txt` at the pinned commit](https://github.com/GNOME/gimp/blob/e101dd19b165f927d3ba0a74658a71537c5661b9/meson_options.txt)

## Log history

| Version | Date       | Summary | Reason |
|---------|------------|---------|--------|
| 0.1.0   | 2026-10-19 | Recorded the release pin and initial plug-in lifecycle/build findings | Establish a traceable baseline before runtime experiments. |
| 0.2.0   | 2026-10-19 | Recorded follow-up protocol, metadata RPC, and local build-prerequisite findings | Clarify the work required for a faithful collector and whether this workspace can execute it. |
| 0.3.0   | 2026-10-19 | Traced host PDB registration interception and plug-in startup/init behavior | Resolve whether interception is valid evidence and identify runtime-dependent procedure registration. |
| 0.4.0   | 2026-10-19 | Clarified what headers provide and what a metadata-preserving shim would need to implement | Distinguish API declarations from runtime/plug-in registration behavior and record the shim as an untested option. |
