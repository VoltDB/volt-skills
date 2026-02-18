# volt-skills

Custom [Claude Code skills](https://code.claude.com/docs/en/skills) for building applications with [Volt Active Data](https://www.voltactivedata.com/) (VoltDB).

## Skills

| Skill                                                                        | Description                                                                                                                  |
|------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| [voltdb-min-client-helper](skills/voltdb-min-client-helper/)                 | Creates minimal VoltDB client Maven projects with scaffolding, dependencies, and build configuration.                        |
| [voltdb-proc-helper](skills/voltdb-proc-helper/)                             | Analyzes data models to recommend partitioning strategies, then generates DDL schemas and stored procedures.                 |
| [voltdb-it-tests-helper](skills/voltdb-it-tests-helper/)                     | Generates integration tests using VoltDB Enterprise Docker testcontainer with realistic test data.                           |
| [voltdb-partitioned-client-helper](skills/voltdb-partitioned-client-helper/) | End-to-end orchestrator that creates complete partitioned VoltDB client applications by coordinating the other three skills. |
| [voltdb-kubernetes](skills/voltdb-kubernetes/)                               | Describes steps to create deployemnt scripts as code.                                                                        |

## Architecture

The skills are designed as composable modules — each can be used independently or combined:

```
voltdb-partitioned-client-helper (orchestrator)
  ├── voltdb-min-client-helper     (Maven project scaffolding)
  ├── voltdb-proc-helper           (partitioning analysis + DDL + procedures)
  └── voltdb-it-tests-helper       (integration tests + test data)
```

**Standalone usage:** Each skill works independently. Use `voltdb-proc-helper` to just get DDL and procedures. Use `voltdb-it-tests-helper` to add tests to an existing project.

**Orchestrated usage:** Use `voltdb-partitioned-client-helper` for a complete guided experience that coordinates all three.

## Repository Structure

```
volt-skills/
├── skills/
│   ├── voltdb-min-client-helper/
│   │   └── SKILL.md
│   ├── voltdb-proc-helper/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── PARTITIONING_FLOWCHART.md
│   ├── voltdb-it-tests-helper/
│   │   └── SKILL.md
│   └── voltdb-partitioned-client-helper/
│       └── SKILL.md
├── LICENSE
└── README.md
```

## What is a Skill?

A skill is a Markdown file (`SKILL.md`) with YAML frontmatter that teaches Claude Code how to perform a specific task. Each skill lives in its own directory under `skills/` and can include supplementary references and scripts.

Minimal skill structure:

```
my-skill/
└── SKILL.md
```

A `SKILL.md` file contains:

```yaml
---
name: my-skill
description: What this skill does and when to use it.
---

Instructions for Claude to follow when this skill is invoked...
```

## Installation

### Per-Project (recommended)

Copy the desired skill directories into your project's `.claude/skills/` folder:

```bash
# Clone this repository
git clone https://github.com/VoltDB/volt-skills.git

# Copy all skills
cp -r volt-skills/skills/voltdb-min-client-helper your-project/.claude/skills/
cp -r volt-skills/skills/voltdb-proc-helper your-project/.claude/skills/
cp -r volt-skills/skills/voltdb-it-tests-helper your-project/.claude/skills/
cp -r volt-skills/skills/voltdb-partitioned-client-helper your-project/.claude/skills/
```

Once installed, invoke a skill by typing its name as a slash command in Claude Code:

```
/voltdb-min-client-helper
/voltdb-proc-helper
/voltdb-it-tests-helper
/voltdb-partitioned-client-helper
```

### Personal (all projects)

To make skills available across all your projects, copy them to `~/.claude/skills/`:

```bash
cp -r volt-skills/skills/voltdb-min-client-helper ~/.claude/skills/
cp -r volt-skills/skills/voltdb-proc-helper ~/.claude/skills/
cp -r volt-skills/skills/voltdb-it-tests-helper ~/.claude/skills/
cp -r volt-skills/skills/voltdb-partitioned-client-helper ~/.claude/skills/
```

## Prerequisites

All skills generate VoltDB client projects that require:

- **Docker** installed and running (for VoltDB testcontainer)
- **Java 17+**
- **Maven 3.6+**
- **VoltDB Enterprise license** file

## Skill Details

### voltdb-min-client-helper

Creates minimal VoltDB client Maven projects:
- Maven project scaffolding (`pom.xml` with VoltDB dependencies)
- Directory structure with proper layout
- Build and verify instructions

### voltdb-proc-helper

Analyzes data models and generates DDL and stored procedures:
- Partitioning strategy analysis (column selection, co-location, lookup tables)
- DDL schema generation with partition declarations
- Stored procedure generation (single-partition and multi-partition)
- Detailed partitioning decision flowcharts (in `references/PARTITIONING_FLOWCHART.md`)

**Key concept:** VoltDB routes single-partition procedure calls based on the FIRST parameter, so the partition key must always be the first parameter in procedure definitions and client calls.

### voltdb-it-tests-helper

Generates integration tests for VoltDB client applications:
- Integration test base class (using [volt-testcontainer](https://github.com/VoltDB/volt-testcontainer))
- Schema-aware test data generator with realistic data
- Integration test classes verifying all procedures
- VoltDB Enterprise Docker testcontainer lifecycle management

### voltdb-partitioned-client-helper

Generates a complete partitioned VoltDB client applications via guided questions.
Acts as an end-to-end orchestrator that provides:
- Interactive guided workflow with clickable options
- Coordinates all three other skills in sequence
- Generates README with partitioning strategy documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
