---
name: voltdb-development
description: Creates complete VoltDB client applications with optimized table partitioning, DDL schemas, stored procedures, and integration tests. Use when user wants to create a VoltDB client, connect to VoltDB, create VoltDB schemas, write VoltDB stored procedures, or write VoltDB integration tests.
---

# VoltDB Development

This skill creates complete VoltDB client applications with optimized partitioning. It generates Maven project scaffolding, analyzes data models for partitioning strategy, creates DDL schemas and stored procedures, and produces integration tests with testcontainer support.

## Rules

Detailed rules are compiled into `AGENTS.md` from the `rules/` directory. Consult `AGENTS.md` for all templates, code examples, and partitioning guidance.

| Priority | Category | Impact | Prefix | Key Rules |
|----------|----------|--------|--------|-----------|
| 1 | Partitioning Strategy | HIGH | `part-` | Partition column selection, co-location, lookup tables, 6 critical rules |
| 2 | DDL & Stored Procedures | HIGH | `ddl-` | DDL syntax, schema templates, all procedure templates |
| 3 | Project Setup | MEDIUM | `proj-` | Maven structure, pom.xml, dependencies, build instructions |
| 4 | Integration Testing | MEDIUM | `test-` | IntegrationTestBase, TestDataGenerator, IT test patterns |
| 5 | Workflow & Templates | MEDIUM | `workflow-` | README.md generation template |

## Workflow

**Use the `AskUserQuestion` tool for each question. This provides clickable options for the user.**

### Step 1: Verify Prerequisites

Before starting any work, verify that all required infrastructure is available. Run these checks using Bash:

```bash
# Check Docker is running
docker info > /dev/null 2>&1
```

- **If Docker is NOT running:** Stop and use `AskUserQuestion` to tell the user:
  - **question:** "Docker is required but not running. Please start Docker and let me know when it's ready."
  - **header:** "Docker"
  - **options:**
    - `Docker is running now` - I've started Docker
    - `Help me start Docker` - Show me how to start it
  - If user selects "Help me start Docker", provide platform-specific instructions:
    - macOS: `open -a Docker`
    - Linux: `sudo systemctl start docker`
  - After user confirms Docker is running, re-verify with `docker info` before proceeding.

```bash
# Check Java 17+
java -version 2>&1
```

- **If Java is not available or below version 17:** Inform the user and stop.

```bash
# Check Maven 3.6+
mvn -version 2>&1
```

- **If Maven is not available:** Inform the user and stop.

**Only proceed to Step 2 after all prerequisites pass.**

### Step 2: Ask License Location

VoltDB Enterprise requires a license file. Use `AskUserQuestion` with:
- **question:** "Where is your VoltDB Enterprise license file?"
- **header:** "License"
- **options:**
  - `VOLTDB_LICENSE env var` (Recommended) - I have VOLTDB_LICENSE environment variable set
  - `/tmp/voltdb-license.xml` - License is at the default location
  - `Specify path` - I'll provide the path to my license file

After the user responds:
1. If `VOLTDB_LICENSE env var`: run `echo $VOLTDB_LICENSE` and verify the file exists at that path using `test -f "$VOLTDB_LICENSE"`.
2. If `/tmp/voltdb-license.xml`: verify the file exists using `test -f /tmp/voltdb-license.xml`.
3. If `Specify path`: ask the user for the path, then verify the file exists.

**If the license file is not found at the specified location**, inform the user and ask them to correct the path. Do not proceed until a valid license file is confirmed.

Save the confirmed license path — it will be used when generating `test.properties`.

### Step 3: Ask Application Name

Use `AskUserQuestion` with:
- **question:** "What should the application be called?"
- **header:** "App name"
- **options:**
  - `my-voltdb-app` (Recommended)
  - `voltdb-client`
  - `data-service`

User can select an option or type their own.

### Step 4: Ask Output Directory

Use `AskUserQuestion` with:
- **question:** "Where should I create the project?"
- **header:** "Directory"
- **options:**
  - `Current directory` (Recommended)
  - `Specify path` - I'll provide a path

### Step 5: Ask Data Model

Use `AskUserQuestion` with:
- **question:** "What type of data model do you need?"
- **header:** "Data model"
- **options:**
  - `Describe custom tables` - I'll describe my tables and columns
  - `Use example model` - Customer/Orders/Product example
  - `Key-Value store` - Simple key-value table (no partitioning analysis needed)

If user selects "Describe custom tables", ask them to describe their tables in a follow-up message.

### Step 6: Analyze and Generate

Apply the rules in `AGENTS.md` to complete the following phases:

**Phase 1 — Partitioning Analysis** (skip for Key-Value):
1. Analyze the data model using `part-*` rules
2. Recommend partition column, co-location groups, lookup tables, and procedure types
3. Present strategy for user confirmation using `AskUserQuestion`:
   - **question:** "Does this partitioning strategy work for you? [strategy summary]"
   - **header:** "Strategy"
   - **options:**
     - `Yes, proceed` (Recommended)
     - `Modify strategy` - I want to change something
     - `Explain more` - Tell me more about the trade-offs

**Phase 2 — Code Generation:**
1. Create Maven project structure (`proj-setup` rules)
2. Generate `schema/ddl.sql` with partition declarations (`ddl-procedures` rules)
3. Generate `schema/remove_db.sql` with DROP statements in correct dependency order (`ddl-procedures` rules)
4. Generate stored procedures under `src/main/java/[package]/procedures/` (`ddl-procedures` rules)
5. Generate `IntegrationTestBase.java` (`test-base-class` rules)
6. Generate `TestDataGenerator.java` and `*IT.java` (`test-data-and-patterns` rules)
7. Generate `test.properties` with testcontainer mode, shutdown enabled, and the confirmed license path from Step 2
8. Generate project `README.md` (`workflow-readme-template` rules)

**Auto-derived defaults (no questions asked):**
- Package name: `com.example.voltdb`
- VoltDB connection mode: testcontainer
- Testcontainer shutdown: yes

### Step 7: Build and Test

After generating the project, automatically build and test:

```bash
cd <project-name> && mvn clean package -DskipTests && mvn verify
```

If the build fails, diagnose the error and fix it. If it succeeds, report the results to the user.
