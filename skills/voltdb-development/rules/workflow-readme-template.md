# README.md Generation Template

> **Category:** Workflow & Templates | **Impact:** MEDIUM

## Context

Every generated VoltDB client project should include a README.md documenting the partitioning strategy, procedures, prerequisites, and build instructions. This template is filled in based on the analysis and generation results.

## Template

**IMPORTANT: Always generate a README.md file in the project root using this template:**

```markdown
# [PROJECT_NAME] - VoltDB Partitioned Client

A VoltDB client demonstrating **table partitioning and co-location** for [brief description].

## Partitioning Strategy

**Partition Key:** `[PARTITION_COLUMN]`

| Table | Partition Column | Strategy |
|-------|------------------|----------|
| [TABLE1] | [PARTITION_COL] | Primary entity |
| [TABLE2] | [PARTITION_COL] | Co-located with [TABLE1] |

### Why [PARTITION_COLUMN]?
- High cardinality (unique per [entity])
- Enables co-location of related tables
- Most queries are [entity]-centric

### Why NOT other columns?
- [LOW_CARD_COL1] - Low cardinality, causes hot spots
- [LOW_CARD_COL2] - Only N values, causes hot spots

## Procedures

| Procedure | Type | Description |
|-----------|------|-------------|
| [Proc1] | Single-partition | [description] |
| [Proc2] | Single-partition | [description] |
| [SearchProc] | Multi-partition | [description] |

## Prerequisites

- Java 17+
- Maven 3.6+
- Docker (running)
- VoltDB Enterprise license

## Build and Test

\`\`\`bash
# 1. Ensure Docker is running
docker info

# 2. Set up license
export VOLTDB_LICENSE=/path/to/license.xml

# 3. Build
mvn clean package -DskipTests

# 4. Run tests
mvn verify
\`\`\`

## Project Structure

\`\`\`
[project-name]/
├── pom.xml
├── README.md
├── schema/ddl.sql
├── src/main/java/[package]/procedures/
│   ├── [Procedure1].java
│   └── ...
└── src/test/java/[package]/
    ├── IntegrationTestBase.java
    ├── TestDataGenerator.java
    └── [TestClass]IT.java
\`\`\`
```

## For Key-Value Projects

Simplify the README by removing the partitioning strategy section and procedure table. Focus on:
- Project description
- Prerequisites
- Build and test commands
- Project structure
