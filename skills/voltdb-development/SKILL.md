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

### Step 1: Ask Application Name

Use `AskUserQuestion` with:
- **question:** "What should the application be called?"
- **header:** "App name"
- **options:**
  - `my-voltdb-app` (Recommended)
  - `voltdb-client`
  - `data-service`

User can select an option or type their own.

### Step 2: Ask Output Directory

Use `AskUserQuestion` with:
- **question:** "Where should I create the project?"
- **header:** "Directory"
- **options:**
  - `Current directory` (Recommended)
  - `Specify path` - I'll provide a path

### Step 3: Ask Data Model

Use `AskUserQuestion` with:
- **question:** "What type of data model do you need?"
- **header:** "Data model"
- **options:**
  - `Describe custom tables` - I'll describe my tables and columns
  - `Use example model` - Customer/Orders/Product example
  - `Key-Value store` - Simple key-value table (no partitioning analysis needed)

If user selects "Describe custom tables", ask them to describe their tables in a follow-up message.

### Step 4: Analyze and Generate

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
3. Generate stored procedures under `src/main/java/[package]/procedures/` (`ddl-procedures` rules)
4. Generate `IntegrationTestBase.java` (`test-base-class` rules)
5. Generate `TestDataGenerator.java` and `*IT.java` (`test-data-and-patterns` rules)
6. Generate `test.properties` with testcontainer mode and shutdown enabled
7. Generate project `README.md` (`workflow-readme-template` rules)

**Auto-derived defaults (no questions asked):**
- Package name: `com.example.voltdb`
- VoltDB connection mode: testcontainer
- Testcontainer shutdown: yes

### Step 5: Build and Test

After generating the project, automatically build and test:

```bash
cd <project-name> && mvn clean package -DskipTests && mvn verify
```

If the build fails, diagnose the error and fix it. If it succeeds, report the results to the user.
