# voltdb-development

A [Claude Code skill](https://claude.ai/docs/claude-code/skills) for building complete VoltDB client applications with optimized table partitioning.

## What It Does

This skill generates a complete, buildable VoltDB client application:

- **Partitioning analysis** — analyzes your data model and recommends partition columns, co-location groups, and lookup tables
- **DDL & stored procedures** — generates `schema/ddl.sql` and Java stored procedures with correct partition key parameter order
- **Maven project** — scaffolds a complete Maven project with `pom.xml`, dependencies, and build configuration
- **Integration tests** — generates `IntegrationTestBase`, `TestDataGenerator`, and `*IT.java` tests using [volt-testcontainer](https://github.com/VoltDB/volt-testcontainer)

## Usage

Invoke the skill in Claude Code:

```
/voltdb-development
```

The skill asks 3 questions:
1. **Application name** (default: `my-voltdb-app`)
2. **Output directory** (default: current directory)
3. **Data model** — describe custom tables, use an example model, or a simple Key-Value store

Then it generates the complete project and runs `mvn verify` to build and test.

## Structure

```
voltdb-development/
├── SKILL.md              # Trigger conditions + guided workflow
├── AGENTS.md             # Compiled rules (generated — do not edit)
├── metadata.json         # Version and references
├── rules/                # Atomic rule files
│   ├── _sections.md      # Category definitions
│   ├── _template.md      # Rule authoring template
│   ├── part-*.md         # Partitioning strategy rules
│   ├── ddl-*.md          # DDL and procedure templates
│   ├── proj-*.md         # Project setup rules
│   ├── test-*.md         # Integration testing rules
│   └── workflow-*.md     # Workflow templates
├── scripts/
│   └── build.sh          # Compiles rules/ → AGENTS.md
└── README.md
```

## Rules

| Priority | Category | Impact | Files |
|----------|----------|--------|-------|
| 1 | Partitioning Strategy | HIGH | `part-choose-column.md`, `part-colocation.md`, `part-lookup-tables.md`, `part-critical-rules.md` |
| 2 | DDL & Stored Procedures | HIGH | `ddl-procedures.md` |
| 3 | Project Setup | MEDIUM | `proj-setup.md` |
| 4 | Integration Testing | MEDIUM | `test-base-class.md`, `test-data-and-patterns.md` |
| 5 | Workflow & Templates | MEDIUM | `workflow-readme-template.md` |

## Building AGENTS.md

After modifying any rule file, recompile `AGENTS.md`:

```bash
./scripts/build.sh
```

## Contributing Rules

1. Copy `rules/_template.md` as a starting point
2. Name the file with the appropriate prefix (`part-`, `ddl-`, `proj-`, `test-`, `workflow-`)
3. Run `./scripts/build.sh` to recompile `AGENTS.md`

## Prerequisites

Generated projects require:
- **Docker** installed and running
- **Java 17+**
- **Maven 3.6+**
- **VoltDB Enterprise license** file
