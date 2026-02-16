---
name: voltdb-partitioned-client-helper
description: Creates complete VoltDB client applications with optimized table partitioning, end-to-end. Orchestrates project scaffolding, partitioning analysis, DDL/procedure generation, and integration test creation. Use when user wants a full partitioned VoltDB client application.
---

# VoltDB Partitioned Client Helper

This skill provides a complete, guided experience for creating a VoltDB client application with optimized partitioning. It orchestrates three other skills to deliver an end-to-end solution.

## How It Works

This skill coordinates:
1. **`voltdb-min-client-helper`** — Maven project scaffolding and `pom.xml`
2. **`voltdb-proc-helper`** — Partitioning analysis, DDL schema, and stored procedures
3. **`voltdb-it-tests-helper`** — Integration tests with testcontainer and realistic data

**Use the `AskUserQuestion` tool for each question. This provides clickable options for the user.**

---

## Step 1: Ask Project Name

Use `AskUserQuestion` with:
- **question:** "What should the project be called?"
- **header:** "Project name"
- **options:**
  - `my-voltdb-app` (example)
  - `voltdb-client`
  - `data-service`

User can select an option or type their own.

---

## Step 2: Ask Package Name

Use `AskUserQuestion` with:
- **question:** "What Java package should I use?"
- **header:** "Package"
- **options:**
  - `com.example.voltdb` (Recommended)
  - `com.mycompany.data`
  - `org.example.db`

---

## Step 3: Ask for Data Model

Use `AskUserQuestion` with:
- **question:** "What type of data model do you need?"
- **header:** "Data model"
- **options:**
  - `Describe custom tables` - I'll describe my tables and columns
  - `Use example model` - Customer/Orders/Product example
  - `Key-Value store` - Simple key-value table

If user selects "Describe custom tables", ask them to describe their tables in a follow-up message.

---

## Step 4: Analyze Partitioning and Generate DDL/Procedures

Follow the instructions in **`voltdb-proc-helper`**:
1. Analyze the data model and recommend a partitioning strategy
2. Present the strategy for user confirmation
3. Generate `schema/ddl.sql` with partition declarations
4. Generate stored procedures under `src/main/java/[package]/procedures/`

---

## Step 5: Ask Output Directory

Use `AskUserQuestion` with:
- **question:** "Where should I create the project?"
- **header:** "Directory"
- **options:**
  - `Current directory` (Recommended)
  - `Specify path` - I'll provide a path

---

## Step 6: Generate Project Scaffolding

Follow the instructions in **`voltdb-min-client-helper`**:
1. Create the project directory structure
2. Generate `pom.xml` with VoltDB dependencies
3. Place the DDL and procedures generated in Step 4

---

## Step 7: Generate Integration Tests

Follow the instructions in **`voltdb-it-tests-helper`**:
1. Generate `IntegrationTestBase.java`
2. Generate `TestDataGenerator.java` with realistic data for the schema
3. Generate `*IT.java` integration test class verifying all procedures
4. Generate `test.properties`

---

## Step 8: Generate README

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

---

## Step 9: Offer to Build and Test

Use `AskUserQuestion`:
- **question:** "Project created. Would you like me to build and test it now?"
- **header:** "Build"
- **options:**
  - `Yes, build and test` (Recommended)
  - `No, I'll build later`
  - `Show build commands` - Just show me the commands

If user selects "Yes", run:
```bash
cd <project-name> && mvn clean package -DskipTests && mvn verify
```
