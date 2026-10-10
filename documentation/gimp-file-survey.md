# GIMP procedure registration survey

This survey records how the GIMP source declares procedures, based on the
`GNOME/gimp` checkout at revision
[`eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463`](https://github.com/GNOME/gimp/commit/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463).
The patterns are not interchangeable, even when they produce similar
procedure metadata at runtime.

## Findings

### Script-Fu Scheme

Procedure declarations are forms in `.scm` files. The source contains
`script-fu-register`, `script-fu-register-procedure`, and
`script-fu-register-filter`; the filter form has both legacy and v3 layouts.
Parameters are written as `SF-*` forms. Menu locations are declared
separately with `script-fu-menu-register`.

For example,
[`paste-as-pattern.scm`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/script-fu/scripts/paste-as-pattern.scm)
registers `script-fu-paste-as-pattern`, its label, description, author, date,
and parameters, then separately assigns `<Image>/Edit/Paste as`.
[`test-i18n.scm`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/script-fu/scripts/test/testi18n/test-i18n.scm)
demonstrates newer procedure registration and translated labels.

The current catalog builder handles `script-fu-register` and
`script-fu-register-filter`, but not `script-fu-register-procedure`. Its filter
parser assumes the legacy positional layout. In the v3 example, position 8
contains `SF-ONE-OR-MORE-DRAWABLE`, not a drawable-type string, so recognizing
the form name alone is not sufficient. Menu registration is an independent
form and must be associated by procedure name.

### Python plug-ins

Python plug-ins subclass `Gimp.PlugIn` and commonly implement
`do_query_procedures()` and `do_create_procedure(name)`. The query method
returns procedure identifiers; creation branches by identifier and calls
language-binding constructors such as `Gimp.Procedure.new`,
`Gimp.LoadProcedure.new`, `Gimp.ExportProcedure.new`, or
`Gimp.ThumbnailProcedure.new`.

[`foggify.py`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/python/foggify.py)
shows a menu procedure with documentation, attribution, arguments, a menu
label, and a separate menu path. The multi-procedure
[`file-openraster.py`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/python/file-openraster.py)
shows load, export, and thumbnail procedure variants.

These are Python API calls, not C spellings. Python registrations need their
own extractor; static analysis must not import or execute plug-in files.

### Plug-in C

Many C plug-ins connect procedure-discovery and creation callbacks on
`GimpPlugInClass`. Common discovery hooks include `query_procedures`; some
plug-ins instead use `init_procedures`. Names may be string literals, macros,
or values assembled in code. Creation can use generic
`gimp_procedure_new()`, load/export constructors, or other specialized
constructors.

- [`help.c`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/help/help.c)
  advertises a macro-defined extension name and creates a persistent generic
  procedure with attribution and string-array arguments.
- [`file-png.c`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/common/file-png.c)
  advertises three names and branches to load/export constructors. It sets
  labels, documentation, attribution, file-format metadata, and export
  arguments.
- [`file-another-rawtherapee.c`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/file-raw/file-another-rawtherapee.c)
  uses `init_procedures` and probes for an external application before
  advertising procedures, so the available set can depend on the environment.
- [`filter-browser.c`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/plug-ins/filter-browser/filter-browser.c)
  uses a generic procedure constructor and a local `procedure_name`, rather
  than a fixed literal at the constructor call.

Consequently, searching for `_PROC`, a single constructor, or a particular
callback spelling is not sufficient to enumerate procedures reliably.
Procedure construction, name discovery, and metadata assignment can be in
different functions, branches, or files.

### Native `app/pdb` C procedures

The built-in PDB has a different registration style. For example,
[`image-guides-cmds.c`](https://github.com/GNOME/gimp/blob/eff4619d3f0e5b4e1313e2d8cdff8ecf51a44463/app/pdb/image-guides-cmds.c)
creates procedures with `gimp_procedure_new(invoker, ...)`, then sets a static
name, help, and attribution, and adds argument/return-value parameter specs.
This is the style the existing native C extractor was written for; it is not
the plug-in registration style above.

### Headers

In the plug-in source tree surveyed, procedure discovery and construction
occur in `.c` and `.py` implementation files. The `.h` files did not contain
the registration callbacks or procedure constructors searched for. Headers
can still define macros, constants, and types used by registrations, so they
may be needed to resolve names, but they are not an independent source of
catalog entries in these examples.

## Menu and plug-in organization

A human-readable menu label and a menu location are distinct:

- C and Python procedures commonly set a label with
  `gimp_procedure_set_menu_label()` / `set_menu_label()`.
- Menu procedures may separately add one or more paths with
  `gimp_procedure_add_menu_path()` / `add_menu_path()`.
- Script-Fu uses the separate `script-fu-menu-register` form.
- File load/export procedures can have useful labels and file-format metadata
  without being ordinary image-menu items.

Therefore a label alone cannot place an item in a menu tree. The catalog
should keep procedure identity, owning plug-in, display label, and menu path
as separate fields. Some procedures have no menu path; some may have multiple
paths. This also explains why menu-oriented plug-in browsing and an
alphabetical procedure lookup need not be the same view.

## Implications for the catalog builder

1. Keep source-format extractors separate (Scheme, Python, C), with shared
   normalization and source-link helpers.
2. Treat native `app/pdb` C and plug-in C as separate registration families.
3. For plug-in C, associate advertised names with constructor/metadata calls
   using function and branch scope; preserve macro/dynamic cases as unsupported
   or unresolved rather than inventing values.
4. Resolve headers when necessary for macros or constants, but do not treat
   header declarations as procedure registrations by themselves.
5. Preserve menu label and menu path separately, and allow absent or multiple
   paths.
6. Regard static parsing as source-based extraction, not a guarantee of the
   runtime PDB. Conditional registration and environment-dependent procedures
   can change what GIMP actually exposes.

## Reproducible search starting points

Run from the repository root after checking out the GIMP source at the
revision above:

```sh
rg -n 'query_procedures|init_procedures|create_procedure|gimp_(load|export)_procedure_new|gimp_procedure_new' \
  tmp/gimp-src/plug-ins --glob '*.c'
rg -n 'do_query_procedures|do_create_procedure|set_menu_label|set_documentation|add_menu_path' \
  tmp/gimp-src/plug-ins/python --glob '*.py'
rg -n 'script-fu-register-procedure|script-fu-register-filter|script-fu-register|script-fu-menu-register' \
  tmp/gimp-src/plug-ins/script-fu/scripts --glob '*.scm'
rg -n 'gimp_object_set_static_name|gimp_procedure_set_static_help|gimp_procedure_add_argument|gimp_procedure_add_return_value' \
  tmp/gimp-src/app/pdb --glob '*.c'
```
