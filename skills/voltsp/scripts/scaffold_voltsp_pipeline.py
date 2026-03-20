#!/usr/bin/env python3
"""Generate deterministic VoltSP starter files from skill templates."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_tokens(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"Refuse to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create deterministic VoltSP Java/YAML starter files."
    )
    parser.add_argument("--out-dir", required=True, help="Output directory")
    parser.add_argument("--pipeline-name", required=True, help="Pipeline display name")
    parser.add_argument(
        "--track",
        choices=("java", "yaml", "both"),
        default="both",
        help="Starter track to generate",
    )
    parser.add_argument("--java-package", default="com.acme.pipeline")
    parser.add_argument("--java-class", default="SamplePipeline")
    parser.add_argument("--schema-version", default="1.7.1")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite generated files when they already exist",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    skill_root = script_dir.parent
    template_root = skill_root / "assets" / "templates"
    out_dir = Path(args.out_dir).resolve()

    package_path = Path(*args.java_package.split("."))
    pipeline_class = f"{args.java_package}.{args.java_class}"

    common_replacements = {
        "__PIPELINE_NAME__": args.pipeline_name,
        "__SCHEMA_VERSION__": args.schema_version,
        "__PIPELINE_CLASS__": pipeline_class,
    }

    generated: list[Path] = []

    runtime_config_tmpl = (template_root / "yaml" / "runtime-config.yaml").read_text(
        encoding="utf-8"
    )
    runtime_config_out = out_dir / "runtime-config.yaml"
    write_file(
        runtime_config_out,
        replace_tokens(runtime_config_tmpl, common_replacements),
        args.force,
    )
    generated.append(runtime_config_out)

    helm_values_tmpl = (template_root / "helm" / "values.yaml").read_text(
        encoding="utf-8"
    )
    helm_values_out = out_dir / "values.yaml"
    write_file(
        helm_values_out,
        replace_tokens(helm_values_tmpl, common_replacements),
        args.force,
    )
    generated.append(helm_values_out)

    if args.track in {"yaml", "both"}:
        pipeline_yaml_tmpl = (
            template_root / "yaml" / "pipeline-definition.yaml"
        ).read_text(encoding="utf-8")
        pipeline_yaml_out = out_dir / "pipeline.yaml"
        write_file(
            pipeline_yaml_out,
            replace_tokens(pipeline_yaml_tmpl, common_replacements),
            args.force,
        )
        generated.append(pipeline_yaml_out)

    if args.track in {"java", "both"}:
        java_tmpl = (template_root / "java" / "Pipeline.java.tmpl").read_text(
            encoding="utf-8"
        )
        java_replacements = {
            **common_replacements,
            "__PACKAGE__": args.java_package,
            "__CLASS__": args.java_class,
        }
        java_out = out_dir / "src" / "main" / "java" / package_path / f"{args.java_class}.java"
        write_file(java_out, replace_tokens(java_tmpl, java_replacements), args.force)
        generated.append(java_out)

        pom_tmpl = (template_root / "maven" / "pom.xml").read_text(
            encoding="utf-8"
        )
        pom_out = out_dir / "pom.xml"
        write_file(
            pom_out,
            replace_tokens(pom_tmpl, common_replacements),
            args.force,
        )
        generated.append(pom_out)

    print("Generated files:")
    for path in sorted(generated):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
