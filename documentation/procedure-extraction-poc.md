# Procedure extraction proof of concept

## Direction

Use GIMP's non-interactive console and `python-fu-eval` batch interpreter to
query the live Procedure Database (PDB). `Gimp.get_pdb()` provides
`query_procedures()` and `lookup_procedure()`. Query with wildcard filters to
discover every procedure without knowing its name in advance. Procedure
objects expose documentation, attribution, menu paths, arguments, and return
values; `Gimp.FileProcedure` exposes file-format metadata. Capture those
values as JSON instead of reconstructing them by parsing C source.

The local GIMP build can be selected with `GIMP=/path/to/gimp-console`.
GitHub Actions cannot rely on a prebuilt GIMP binary, so the eventual workflow
must build GIMP from source before running the query. Do not assume the binary
used locally is available in CI.

## POC scope

1. Run the batch query with a local GIMP installation.
2. Verify the full export includes the procedures identified in
   [`help.c`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/help/help.c)
   and
   [`file-png.c`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/common/file-png.c),
   including their available metadata.
3. Add a `Makefile` target to build/run the repeatable POC and write its
   captured output to JSON.
4. Record the required GIMP build/runtime setup and assess whether the same
   approach is practical in GitHub Actions.

## Boundaries

- Treat the live PDB as the source of extracted metadata; do not add a
  source-text C parser as a substitute.
- Keep the experiment in `scripts/capture_pdb_poc.py`, separate from
  `scripts/build_pdb.py`; it is not yet part of catalog generation.
- Keep this as a two-file POC. General catalog integration and wider
  registration coverage are later work.
- Do not require a prebuilt/final GIMP binary in GitHub Actions; build from
  source there if the POC is viable.

## Open question

Run `make pdb-poc GIMP=/path/to/gimp-console` in an environment with GIMP 3
and its Python batch interpreter installed. The source documents this
`--batch-interpreter=python-fu-eval` mechanism, but this workspace has no GIMP
executable, so the live invocation and returned Python GI value shapes remain
unverified here. The target procedure set must exist in the selected GIMP
PDB; otherwise the script reports the missing procedures and fails.

The capture script queries all procedures and sorts them by name for stable
output. Each record includes general procedure metadata, arguments, return
values, menu paths, and file metadata when the procedure is a
`Gimp.FileProcedure`. Output defaults to `tmp/pdb-poc.json` and can be changed
with `PDB_POC_OUTPUT=...`.

## Usage

```sh
make pdb-poc GIMP=/path/to/gimp-console
```

To run the export with a Flatpak installation from the repository root:

```sh
flatpak run --filesystem="$PWD" \
  --env=PDB_POC_OUTPUT="$PWD/tmp/pdb-poc.json" \
  org.gimp.GIMP \
  --batch-interpreter=python-fu-eval \
  -b "exec(open('$PWD/scripts/capture_pdb_poc.py', encoding='utf-8').read())" \
  --quit
```

The Flatpak filesystem override lets GIMP read the checked-out script and
write the JSON output inside the repository. This export enumerates the PDB
after GIMP has loaded its procedures; it does not intercept plug-in
registration calls.
