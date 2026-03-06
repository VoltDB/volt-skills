# volt-skills

Custom [Claude Code skills](https://claude.ai/docs/claude-code/skills) for building [Volt Active Data](https://www.voltactivedata.com/) platform applications: VoltDB or VoltSP.

## Skills

| Skill                                            | Description                                                                                                                          |
|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| [voltdb-development](skills/voltdb-development/) | Creates complete VoltDB client applications with optimized partitioning, DDL schemas, stored procedures, and integration tests.      |
| [voltsp](skills/voltsp)                          | Build, test, and troubleshoot Volt Stream Processing pipelines using Java or YAML APIs. Deploy using bare metal (CLI) or Kubernetes. |
| [voltdb-kubernetes](skills/volt-kubernetes/)     | Describes steps to create deployemnt scripts as code.                                                                                |

## What is a Skill?

A skill is a Markdown file (`SKILL.md`) with a header that tells an AI agent (like Claude Code or Codex) how to perform a specific task. It follows the [Agent Skills open standard](https://agentskills.io).

## Installation

### Per-Project (recommended)

Copy the skill directory into your agent's skills folder ([Claude](https://code.claude.com/docs/en/skills#where-skills-live), [Codex](https://developers.openai.com/codex/skills/#where-to-save-skills)):

```bash
# Clone this repository
git clone https://github.com/VoltDB/volt-skills.git

# Copy the skill
cp -r volt-skills/skills/voltdb-development your-project/.claude/skills/
```

Once installed, the agen should be able to pick it up automatically when facing a relevant task. 

Sometimes it is possible to nudge it, e.g. in Claude Code invoke one directly with `/skill-name`:

```
/voltdb-development
```

## Prerequisites

Generated projects typically require:

- **Docker** installed and running (for VoltDB testcontainer)
- **Java 17+**
- **Maven 3.6+**
- **VoltDB/VoltSP Enterprise license** file

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
