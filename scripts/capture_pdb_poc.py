import json
import os
from pathlib import Path

import gi

gi.require_version("Gimp", "3.0")
from gi.repository import Gimp


def serialize_parameter(parameter):
    value_type = parameter.value_type
    return {
        "name": parameter.name,
        "type": value_type.name if value_type else "",
        "label": parameter.nick or "",
        "description": parameter.blurb or "",
    }


def serialize_procedure(name, procedure):
    if procedure is None:
        raise RuntimeError(f"Procedure is not present in this GIMP PDB: {name}")

    menu_paths = procedure.get_menu_paths() or []
    record = {
        "procedure": procedure.get_name(),
        "kind": procedure.get_proc_type().value_nick,
        "title": procedure.get_menu_label() or procedure.get_name(),
        "description": procedure.get_blurb() or "",
        "help": procedure.get_help() or "",
        "helpId": procedure.get_help_id() or "",
        "author": procedure.get_authors() or "",
        "copyright": procedure.get_copyright() or "",
        "date": procedure.get_date() or "",
        "imageTypes": procedure.get_image_types() or "",
        "menuPaths": list(menu_paths),
        "parameters": [
            serialize_parameter(parameter)
            for parameter in procedure.get_arguments()
        ],
        "returnValues": [
            serialize_parameter(parameter)
            for parameter in procedure.get_return_values()
        ],
    }

    if isinstance(procedure, Gimp.FileProcedure):
        record["fileMetadata"] = {
            "formatName": procedure.get_format_name() or "",
            "mimeTypes": procedure.get_mime_types() or "",
            "extensions": procedure.get_extensions() or "",
            "magics": procedure.get_magics() or "",
        }

    return record


pdb = Gimp.get_pdb()
procedure_names = sorted(
    pdb.query_procedures(".*", ".*", ".*", ".*", ".*", ".*", ".*", ".*")
)
if not procedure_names:
    raise RuntimeError("The GIMP PDB query returned no procedures")

records = []
for name in procedure_names:
    procedure = pdb.lookup_procedure(name)
    if procedure is None:
        raise RuntimeError(f"Procedure disappeared from the GIMP PDB during capture: {name}")
    records.append(serialize_procedure(name, procedure))

output = Path(os.environ.get("PDB_POC_OUTPUT", "tmp/pdb-poc.json"))
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Captured {len(records)} procedures to {output}")
