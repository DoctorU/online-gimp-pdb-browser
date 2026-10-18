# GIMP Procedure Browser

The GIMP Procedure Browser is a browsable online reference to GIMP's Procedure
Database (PDB), for GIMP developers and plug-in authors. The long-term goal is
to make the procedures that are available to scripts and plug-ins easier to discover,
understand, and relate to their source. Visitors can keep the reference open
in a web browser and look up procedures without installing or running GIMP
locally.

The program aims to provide a reliable, versioned catalog of GIMP's built-in
procedures, including native `app/pdb` C procedures, built-in C plug-ins, and
built-in Python and Script-Fu procedures. The intended reference tracks the
latest stable GIMP 3 release and records the exact GIMP revision used to build
each catalog.

Extraction methods are still being investigated. In particular, the project
has not established whether a lightweight registration collector can capture
both native and plug-in C procedures, or whether validating it requires a
normal GIMP runtime. See the program plan for goals and the Phase 1 plan for
the current investigation and delivery scope.

## Plans and investigation

- [Program goals and roadmap](documentation/plan/program.md)
- [Phase 0: Existing browser and catalog baseline](documentation/plan/phase0.md)
- [Phase 1: C procedure extraction](documentation/plan/phase1.md)
- [Registration patterns in GIMP source](documentation/gimp-file-survey.md)
- [Live PDB capture proof of concept](documentation/procedure-extraction-poc.md)

The live-PDB proof of concept queries procedures after GIMP has loaded them. It
is an experiment for observing available metadata, not a registration-call
interceptor or the settled catalog-generation architecture.

## Current catalog and local preview

The website is static and reads its catalog from `data/pdb.json`. The existing
builder generates the current catalog from GIMP's Script-Fu sources and native
`app/pdb` C sources. To rebuild it from a GIMP checkout:

```sh
git clone --depth 1 https://github.com/GNOME/gimp.git /tmp/gimp
python3 scripts/build_pdb.py \
  --source-dir /tmp/gimp/plug-ins/script-fu/scripts \
  --pdb-c-dir /tmp/gimp/app/pdb \
  --revision "$(git -C /tmp/gimp rev-parse HEAD)"
```

From the repository root, start a local HTTP server:

```sh
python3 -m http.server 8000
```

Then open <http://localhost:8000>. This existing source-based builder is
separate from the registration-collector experiments proposed for Phase 1;
the proposed collector and its CI workflow are not yet implemented.

## License

The project is licensed under GPL-3.0-or-later. See [LICENSE](LICENSE).
