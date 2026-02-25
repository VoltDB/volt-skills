#!/usr/bin/env python3
"""Perform deterministic structural checks for VoltSP YAML files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

TOP_KEY_PATTERN = re.compile(r"^([A-Za-z0-9_.\-$]+)\s*:\s*(.*?)\s*$")
PIPELINE_DEF_KEYS = {"$schema", "version", "name", "source", "processors", "sink", "resources", "logging"}


def strip_comment(line: str) -> str:
    if "#" not in line:
        return line.rstrip("\n")
    return line.split("#", 1)[0].rstrip("\n")


def read_top_level(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = strip_comment(raw_line)
        if not line.strip():
            continue
        if line[0].isspace():
            continue
        match = TOP_KEY_PATTERN.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            if key not in result:
                result[key] = value
    return result


def normalized_scalar(value: str) -> str:
    return value.strip().strip("'").strip('"')


def check_definition(path: Path, errors: list[str]) -> None:
    data = read_top_level(path)
    required = {"version", "name", "source", "sink"}
    missing = sorted(required - set(data))
    if missing:
        errors.append(
            f"{path}: missing required top-level keys: {', '.join(missing)}"
        )

    if "version" in data and normalized_scalar(data["version"]) != "1":
        errors.append(f"{path}: version must be 1 in pipeline definition")

    if "streaming" in data:
        errors.append(
            f"{path}: top-level 'streaming' found; this looks like Helm values, not pipeline definition"
        )


def check_runtime_config(path: Path, errors: list[str]) -> None:
    data = read_top_level(path)
    wrong = sorted(set(data).intersection(PIPELINE_DEF_KEYS))
    if wrong:
        errors.append(
            f"{path}: contains pipeline-definition keys at top level: {', '.join(wrong)}"
        )


def check_helm_values(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    top = read_top_level(path)
    if "streaming" not in top:
        errors.append(f"{path}: missing top-level 'streaming' key")
    if not re.search(r"(?m)^\s*streaming\s*:\s*$", text):
        errors.append(f"{path}: malformed 'streaming' section")
    if not re.search(r"(?m)^\s{2,}pipeline\s*:\s*$", text):
        errors.append(f"{path}: missing 'streaming.pipeline' section")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate VoltSP pipeline definition, runtime config, and Helm values separation."
    )
    parser.add_argument("--definition", required=True, help="Path to pipeline definition YAML")
    parser.add_argument("--config", help="Optional runtime config YAML")
    parser.add_argument("--helm-values", help="Optional Helm values YAML")
    args = parser.parse_args()

    errors: list[str] = []
    definition_path = Path(args.definition).resolve()
    if not definition_path.exists():
        errors.append(f"{definition_path}: file does not exist")
    else:
        check_definition(definition_path, errors)

    if args.config:
        config_path = Path(args.config).resolve()
        if not config_path.exists():
            errors.append(f"{config_path}: file does not exist")
        else:
            check_runtime_config(config_path, errors)

    if args.helm_values:
        helm_path = Path(args.helm_values).resolve()
        if not helm_path.exists():
            errors.append(f"{helm_path}: file does not exist")
        else:
            check_helm_values(helm_path, errors)

    if errors:
        print("Layout check failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Layout check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
