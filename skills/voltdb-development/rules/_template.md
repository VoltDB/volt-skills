# Rule Authoring Template

Use this template when adding a new rule file to `rules/`.

## File naming convention

```
<prefix>-<short-name>.md
```

Prefixes map to categories defined in `_sections.md`:
- `part-` — Partitioning Strategy
- `ddl-` — DDL & Stored Procedures
- `proj-` — Project Setup
- `test-` — Integration Testing
- `workflow-` — Workflow & Templates

## Template

```markdown
# <Rule Title>

> **Category:** <category name> | **Impact:** HIGH / MEDIUM / LOW

## Context

Why this rule exists and when it applies.

## Rule

The prescriptive guidance.

## Examples

Concrete code or DDL examples showing correct and incorrect usage.

## References

Links to VoltDB documentation or related rules.
```

## After adding a rule

Run the build script to recompile `AGENTS.md`:

```bash
./scripts/build.sh
```
