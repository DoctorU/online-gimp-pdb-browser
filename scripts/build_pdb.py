#!/usr/bin/env python3
"""Build a static JSON index from GIMP's Script-Fu Scheme sources."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


@dataclass(frozen=True)
class StringLiteral:
    value: str


def tokenize(source: str) -> Iterator[Any]:
    index = 0
    while index < len(source):
        char = source[index]
        if char.isspace():
            index += 1
        elif char == ";":
            newline = source.find("\n", index)
            index = len(source) if newline == -1 else newline + 1
        elif char == '"':
            index += 1
            value: list[str] = []
            while index < len(source) and source[index] != '"':
                if source[index] == "\\" and index + 1 < len(source):
                    index += 1
                    value.append({"n": "\n", "t": "\t", "r": "\r"}.get(source[index], source[index]))
                else:
                    value.append(source[index])
                index += 1
            if index < len(source):
                index += 1
            yield StringLiteral("".join(value))
        elif char in "()'":
            yield char
            index += 1
        else:
            end = index + 1
            while end < len(source) and not source[end].isspace() and source[end] not in "();'\"":
                end += 1
            yield source[index:end]
            index = end


def tokenize_c(source: str) -> list[Any]:
    tokens = []
    index = 0
    escapes = {"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f", "v": "\v"}
    while index < len(source):
        if source[index].isspace():
            index += 1
        elif source.startswith("//", index):
            newline = source.find("\n", index)
            index = len(source) if newline < 0 else newline + 1
        elif source.startswith("/*", index):
            end = source.find("*/", index + 2)
            index = len(source) if end < 0 else end + 2
        elif source[index] in {'"', "'"}:
            quote = source[index]
            index += 1
            value = []
            while index < len(source) and source[index] != quote:
                if source[index] == "\\" and index + 1 < len(source):
                    index += 1
                    if source[index] == "\n":
                        index += 1
                        continue
                    value.append(escapes.get(source[index], source[index]))
                else:
                    value.append(source[index])
                index += 1
            index = min(index + 1, len(source))
            tokens.append(StringLiteral("".join(value)))
        elif source[index].isalnum() or source[index] == "_":
            end = index + 1
            while end < len(source) and (source[end].isalnum() or source[end] == "_"):
                end += 1
            tokens.append(source[index:end])
            index = end
        else:
            tokens.append(source[index])
            index += 1
    return tokens


def c_call_arguments(tokens: list[Any], name: str, start: int = 0, end: int | None = None) -> list[tuple[int, list[list[Any]]]]:
    end = len(tokens) if end is None else end
    calls = []
    index = start
    while index + 1 < end:
        if tokens[index] != name or tokens[index + 1] != "(":
            index += 1
            continue
        args = []
        argument = []
        parens = brackets = braces = 0
        cursor = index + 2
        while cursor < end:
            token = tokens[cursor]
            if token == "(" :
                parens += 1
            elif token == ")":
                if parens == brackets == braces == 0:
                    if argument or args:
                        args.append(argument)
                    break
                parens -= 1
            elif token == "[":
                brackets += 1
            elif token == "]":
                brackets -= 1
            elif token == "{":
                braces += 1
            elif token == "}":
                braces -= 1
            if token == "," and parens == brackets == braces == 0:
                args.append(argument)
                argument = []
            else:
                argument.append(token)
            cursor += 1
        calls.append((index, args))
        index = cursor + 1
    return calls


def c_text(expression: list[Any]) -> str:
    if expression and all(isinstance(token, StringLiteral) for token in expression):
        return "".join(token.value for token in expression)
    return " ".join(token.value if isinstance(token, StringLiteral) else str(token) for token in expression).strip()


def c_string_argument(arguments: list[list[Any]], index: int) -> str:
    return c_text(arguments[index]) if index < len(arguments) else ""


def c_parameter(expression: list[Any]) -> dict[str, Any] | None:
    for index, token in enumerate(expression[:-1]):
        if isinstance(token, str) and token.startswith("gimp_param_spec_") and expression[index + 1] == "(":
            calls = c_call_arguments(expression, token, index, len(expression))
            if not calls:
                return None
            arguments = calls[0][1]
            return {
                "type": token.removeprefix("gimp_param_spec_"),
                "label": c_string_argument(arguments, 1),
                "description": c_string_argument(arguments, 2),
                "details": [c_text(value) for value in arguments[3:] if c_text(value)],
            }
    return None


def native_procedures(source_dir: Path, revision: str, repository: str, source_prefix: str) -> list[dict[str, Any]]:
    procedures = []
    for path in sorted(source_dir.rglob("*.c")):
        tokens = tokenize_c(path.read_text(encoding="utf-8", errors="replace"))
        registrations = c_call_arguments(tokens, "gimp_procedure_new")
        for number, (start, _) in enumerate(registrations):
            end = registrations[number + 1][0] if number + 1 < len(registrations) else len(tokens)
            names = c_call_arguments(tokens, "gimp_object_set_static_name", start, end)
            helps = c_call_arguments(tokens, "gimp_procedure_set_static_help", start, end)
            attributions = c_call_arguments(tokens, "gimp_procedure_set_static_attribution", start, end)
            if not names or len(names[0][1]) < 2:
                continue
            name = c_string_argument(names[0][1], 1)
            if not name.startswith("gimp-"):
                continue
            help_args = helps[0][1] if helps else []
            attribution_args = attributions[0][1] if attributions else []
            parameters = []
            return_values = []
            for function, destination in (
                ("gimp_procedure_add_argument", parameters),
                ("gimp_procedure_add_return_value", return_values),
            ):
                for _, call_args in c_call_arguments(tokens, function, start, end):
                    if len(call_args) > 1:
                        parameter = c_parameter(call_args[1])
                        if parameter:
                            destination.append(parameter)
            relative_path = f"{source_prefix.strip('/')}/{path.relative_to(source_dir).as_posix()}"
            procedures.append({
                "procedure": name,
                "title": name,
                "shortcut": "",
                "description": c_string_argument(help_args, 1),
                "help": c_string_argument(help_args, 2),
                "author": c_string_argument(attribution_args, 1),
                "copyright": c_string_argument(attribution_args, 2),
                "authorEmail": "",
                "date": c_string_argument(attribution_args, 3),
                "imageTypes": "",
                "drawableTypes": "",
                "menuPath": "",
                "parameters": parameters,
                "returnValues": return_values,
                "kind": "native-pdb",
                "sourcePath": relative_path,
                "source": f"{repository}/blob/{revision}/{relative_path}",
            })
    return procedures


def parse_expression(tokens: list[Any], index: int) -> tuple[Any, int]:
    token = tokens[index]
    if token == "(":
        values = []
        index += 1
        while index < len(tokens) and tokens[index] != ")":
            value, index = parse_expression(tokens, index)
            values.append(value)
        return values, min(index + 1, len(tokens))
    if token == "'":
        value, index = parse_expression(tokens, index + 1)
        return ["quote", value], index
    if token == "_" and index + 1 < len(tokens) and isinstance(tokens[index + 1], StringLiteral):
        return tokens[index + 1], index + 2
    return token, index + 1


def read_forms(source: str) -> Iterator[list[Any]]:
    tokens = list(tokenize(source))
    index = 0
    while index < len(tokens):
        if tokens[index] == "(":
            form, index = parse_expression(tokens, index)
            if isinstance(form, list):
                yield form
        else:
            index += 1


def scheme_repr(value: Any) -> str:
    if isinstance(value, StringLiteral):
        return json.dumps(value.value, ensure_ascii=False)
    if isinstance(value, list):
        if value and value[0] == "quote" and len(value) == 2:
            return "'" + scheme_repr(value[1])
        return "(" + " ".join(scheme_repr(item) for item in value) + ")"
    return str(value)


def text_value(value: Any) -> str:
    return value.value if isinstance(value, StringLiteral) else str(value)


def without_mnemonic(value: str) -> str:
    return re.sub(r"(?<!_)_([A-Za-z0-9])", r"\1", value).replace("__", "_")


def procedure_record(form: list[Any], source_path: str, source_url: str, menu_paths: dict[str, str]) -> dict[str, Any] | None:
    if not form or form[0] not in {"script-fu-register-filter", "script-fu-register"} or len(form) < 7:
        return None

    procedure = text_value(form[1])
    menu_label = text_value(form[2])
    shortcut_match = re.search(r"(?<!_)_([A-Za-z0-9])", menu_label)
    title = without_mnemonic(menu_label)
    authors = text_value(form[4])
    email_match = re.search(r"<([^>]+)>", authors)
    drawable_types = text_value(form[8]) if form[0] == "script-fu-register-filter" and len(form) > 8 else ""
    parameter_start = 9 if form[0] == "script-fu-register-filter" else 7
    parameters = []
    index = parameter_start
    while index < len(form):
        parameter_type = form[index]
        if not isinstance(parameter_type, str) or not parameter_type.startswith("SF-"):
            index += 1
            continue
        end = index + 1
        while end < len(form) and not (isinstance(form[end], str) and form[end].startswith("SF-")):
            end += 1
        values = form[index + 1:end]
        parameters.append({
            "type": parameter_type,
            "label": without_mnemonic(text_value(values[0])) if values else "",
            "details": [scheme_repr(value) for value in values[1:]],
        })
        index = end

    return {
        "procedure": procedure,
        "title": title,
        "shortcut": shortcut_match.group(1).upper() if shortcut_match else "",
        "description": text_value(form[3]),
        "author": text_value(form[5]),
        "authorEmail": email_match.group(1) if email_match else "",
        "date": text_value(form[6]),
        "imageTypes": text_value(form[7]) if len(form) > 7 else "",
        "drawableTypes": drawable_types,
        "menuPath": menu_paths.get(procedure, ""),
        "parameters": parameters,
        "returnValues": [],
        "kind": "script-fu",
        "sourcePath": source_path,
        "source": source_url,
    }


def build_index(
    source_dir: Path,
    revision: str,
    repository: str,
    source_prefix: str,
    pdb_c_dir: Path | None,
    pdb_c_prefix: str,
) -> dict[str, Any]:
    registrations: list[tuple[list[Any], str, str]] = []
    menu_paths: dict[str, str] = {}
    for path in sorted(source_dir.rglob("*.scm")):
        source = path.read_text(encoding="utf-8", errors="replace")
        relative_path = f"{source_prefix.strip('/')}/{path.relative_to(source_dir).as_posix()}"
        source_url = f"{repository}/blob/{revision}/{relative_path}"
        for form in read_forms(source):
            if form and form[0] == "script-fu-menu-register" and len(form) > 2:
                menu_paths[text_value(form[1])] = text_value(form[2])
            elif form and form[0] in {"script-fu-register-filter", "script-fu-register"}:
                registrations.append((form, relative_path, source_url))

    procedures = []
    seen = set()
    for form, path, source_url in registrations:
        record = procedure_record(form, path, source_url, menu_paths)
        if record and record["procedure"] not in seen:
            procedures.append(record)
            seen.add(record["procedure"])
    if pdb_c_dir:
        for record in native_procedures(pdb_c_dir, revision, repository, pdb_c_prefix):
            if record["procedure"] not in seen:
                procedures.append(record)
                seen.add(record["procedure"])
    procedures.sort(key=lambda item: item["procedure"].casefold())
    return {
        "revision": revision,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceRepository": repository,
        "procedures": procedures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True, help="Root directory containing Script-Fu .scm files")
    parser.add_argument("--output", type=Path, default=Path("data/pdb.json"), help="Generated JSON index path")
    parser.add_argument("--revision", required=True, help="GIMP source commit SHA used for the index")
    parser.add_argument("--repository", default="https://github.com/GNOME/gimp", help="GIMP source repository URL")
    parser.add_argument("--source-prefix", default="plug-ins/script-fu/scripts", help="Path prefix for source links")
    parser.add_argument("--pdb-c-dir", type=Path, help="Root of GIMP's native app/pdb C sources")
    parser.add_argument("--pdb-c-prefix", default="app/pdb", help="Path prefix for native PDB source links")
    args = parser.parse_args()
    index = build_index(args.source_dir, args.revision, args.repository, args.source_prefix, args.pdb_c_dir, args.pdb_c_prefix)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Indexed {len(index['procedures'])} procedures from {args.revision}")


if __name__ == "__main__":
    main()