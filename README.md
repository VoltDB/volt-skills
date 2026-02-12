# volt-skills

Custom [Claude Code skills](https://code.claude.com/docs/en/skills) for building applications with [Volt Active Data](https://www.voltactivedata.com/) (VoltDB).

## Skills

| Skill | Description |
|-------|-------------|
| [voltdb-client-helper](skills/voltdb-client-helper/) | Creates VoltDB client applications with connection code, DDL schemas, stored procedures, and integration tests. |
| [voltdb-partitioned-client](skills/voltdb-partitioned-client/) | Creates VoltDB client applications with optimized table partitioning, co-located procedures, and partition-aware CRUD/search operations. Extends `voltdb-client-helper`. |

## Repository Structure

```
volt-skills/
├── skills/
│   ├── voltdb-client-helper/
│   │   └── SKILL.md
│   └── voltdb-partitioned-client/
│       ├── SKILL.md
│       └── references/
│           └── PARTITIONING_FLOWCHART.md
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

# Copy a skill into your project
cp -r volt-skills/skills/voltdb-client-helper your-project/.claude/skills/
cp -r volt-skills/skills/voltdb-partitioned-client your-project/.claude/skills/
```

Once installed, invoke a skill by typing its name as a slash command in Claude Code:

```
/voltdb-client-helper
/voltdb-partitioned-client
```

### Personal (all projects)

To make a skill available across all your projects, copy it to `~/.claude/skills/`:

```bash
cp -r volt-skills/skills/voltdb-client-helper ~/.claude/skills/
cp -r volt-skills/skills/voltdb-partitioned-client ~/.claude/skills/
```

## Prerequisites

Both skills generate VoltDB client projects that require:

- **Docker** installed and running (for VoltDB testcontainer)
- **Java 17+**
- **Maven 3.6+**
- **VoltDB Enterprise license** file

## Skill Details

### voltdb-client-helper

Guides you through creating a complete VoltDB client application with:
- Maven project scaffolding (`pom.xml` with VoltDB dependencies)
- DDL schema generation (`schema/ddl.sql`)
- Java stored procedures (using `volt-procedure-api`)
- Integration test base class (using [volt-testcontainer](https://github.com/VoltDB/volt-testcontainer))
- Test data generator
- Integration tests with `VoltDBCluster`
- Build and verify instructions

### voltdb-partitioned-client

Extends `voltdb-client-helper` with partition-aware capabilities:
- Interactive partitioning strategy analysis based on your data model
- Partition column selection guidance (cardinality, query patterns, immutability)
- Co-located table design for efficient single-partition joins
- Lookup table patterns for cross-partition queries
- Single-partition and multi-partition procedure generation
- Detailed partitioning decision flowcharts (in `references/PARTITIONING_FLOWCHART.md`)

**Key concept:** VoltDB routes single-partition procedure calls based on the FIRST parameter, so the partition key must always be the first parameter in procedure definitions and client calls.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
