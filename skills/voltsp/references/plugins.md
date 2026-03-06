# Plugins Guide (Sources, Sinks, Processors)

Use this file as the entry point for plugin/operator selection.

## Workflow

1. Open `references/plugins-catalog.md`.
2. Pick operator by type (`source`, `sink`, `processor`) and use case.
3. If operator is in the priority set, open its detailed file under:
- `references/plugins/sources/<name>.md`
- `references/plugins/sinks/<name>.md`
- `references/plugins/processors/<name>.md`
4. If operator is catalog-only, provide minimal guidance from catalog and note that details are pending.

## Detailed plugin coverage in this skill

Priority set includes dedicated docs for:

- Sources: `stdin`, `file`, `collection`, `generate`, `kafka`, `network`, `mqtt`, `beats`
- Sinks: `stdout`, `blackhole`, `file`, `kafka`, `network`, `elastic`, `syslog`, `mqtt`, `voltdb-procedure`, `voltdb-bulk-insert`
- Processors: `javascript`, `java`, `python`, `voltdb-cache`, `onnx`, `onnx-genai`

## Plugin file format

Each plugin file follows this structure:

1. Title and description
2. Compile dependency
3. Java example (actual API calls)
4. YAML example (actual config)
5. Properties (with types, defaults, required markers)
