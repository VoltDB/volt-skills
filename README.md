# volt-skills

Custom [Claude Code skills](https://claude.ai/docs/claude-code/skills) for building applications with [Volt Active Data](https://www.voltactivedata.com/) (VoltDB).

## Skills

| Skill | Description                                                                                                                     |
|-------|---------------------------------------------------------------------------------------------------------------------------------|
| [voltdb-development](skills/voltdb-development/) | Creates complete VoltDB client applications with optimized partitioning, DDL schemas, stored procedures, and integration tests. |
| [voltdb-kubernetes](skills/volt-kubernetes/)                               | Describes steps to create deployemnt scripts as code.|

## How It Works

The `voltdb-development` skill provides a guided workflow that generates a complete, buildable VoltDB client application:

1. **Verifies prerequisites** — checks Docker, Java, Maven are available
2. **Asks for license location** — confirms VoltDB Enterprise license file path
3. **Asks 3 questions** — application name, output directory, and data model
4. **Analyzes partitioning** — recommends partition columns, co-location groups, and lookup tables
5. **Generates everything** — Maven project, DDL schema (`ddl.sql` + `remove_db.sql`), stored procedures, integration tests, and README
6. **Builds and tests** — runs `mvn verify` to compile, start a VoltDB testcontainer, and run integration tests

## Repository Structure

```
volt-skills/
├── skills/
│   └── voltdb-development/
│       ├── SKILL.md              # Skill entry point — workflow + rule references
│       └── rules/                # Rule files (read on demand by the LLM)
│           ├── _sections.md      # Category definitions
│           ├── _template.md      # Rule authoring template
│           ├── part-*.md         # Partitioning strategy rules
│           ├── ddl-*.md          # DDL and procedure templates
│           ├── proj-*.md         # Project setup rules
│           ├── test-*.md         # Integration testing rules
│           └── workflow-*.md     # Workflow templates
├── LICENSE
└── README.md
```

## What is a Skill?

A skill is a Markdown file (`SKILL.md`) with YAML frontmatter that teaches Claude Code how to perform a specific task. It follows the [Agent Skills open standard](https://agentskills.io). The `voltdb-development` skill uses **progressive disclosure** — `SKILL.md` is the entry point and references individual rule files in `rules/` that the LLM reads on demand as each workflow phase requires them.

## Installation

### Per-Project (recommended)

Copy the skill directory into your project's `.claude/skills/` folder:

```bash
# Clone this repository
git clone https://github.com/VoltDB/volt-skills.git

# Copy the skill
cp -r volt-skills/skills/voltdb-development your-project/.claude/skills/
```

Once installed, invoke the skill in Claude Code:

```
/voltdb-development
```

### Personal (all projects)

To make the skill available across all your projects, copy it to `~/.claude/skills/`:

```bash
cp -r volt-skills/skills/voltdb-development ~/.claude/skills/
```

## Prerequisites

Generated projects require:

- **Docker** installed and running (for VoltDB testcontainer)
- **Java 17+**
- **Maven 3.6+**
- **VoltDB Enterprise license** file

## Contributing Rules

1. Copy `rules/_template.md` as a starting point
2. Name the file with the appropriate prefix (`part-`, `ddl-`, `proj-`, `test-`, `workflow-`)

See `rules/_sections.md` for category definitions and priority order.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
