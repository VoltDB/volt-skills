---
name: voltdb-development
description: Creates complete VoltDB client applications with optimized table partitioning, DDL schemas, stored procedures, and integration tests. Use when user wants to create a VoltDB client, connect to VoltDB, create VoltDB schemas, write VoltDB stored procedures, or write VoltDB integration tests.
metadata:
  version: "1.0.0"
  organization: VoltDB
  references:
    - https://docs.voltactivedata.com/
    - https://github.com/VoltDB/volt-testcontainer
---

# VoltDB Development

This skill creates complete VoltDB client applications with optimized partitioning. It generates Maven project scaffolding, analyzes data models for partitioning strategy, creates DDL schemas and stored procedures, and produces integration tests with testcontainer support.

## Rules

Rules are organized in the `rules/` directory. Read only the rule files needed for the current phase — do NOT read all rules upfront.

| Priority | Category | Impact | Rule Files |
|----------|----------|--------|------------|
| 1 | Partitioning Strategy | HIGH | [rules/part-critical-rules.md](rules/part-critical-rules.md), [rules/part-choose-column.md](rules/part-choose-column.md), [rules/part-colocation.md](rules/part-colocation.md), [rules/part-lookup-tables.md](rules/part-lookup-tables.md) |
| 2 | DDL & Stored Procedures | HIGH | [rules/ddl-procedures.md](rules/ddl-procedures.md), [rules/ddl-multi-step-transactions.md](rules/ddl-multi-step-transactions.md) |
| 3 | Project Setup | MEDIUM | [rules/proj-setup.md](rules/proj-setup.md) |
| 4 | Integration Testing | MEDIUM | [rules/test-base-class.md](rules/test-base-class.md), [rules/test-data-and-patterns.md](rules/test-data-and-patterns.md) |
| 5 | Workflow & Templates | MEDIUM | [rules/workflow-readme-template.md](rules/workflow-readme-template.md) |

## Workflow

**Use the `AskUserQuestion` tool for each question. This provides clickable options for the user.**

### Step 1: Verify Docker is Running (silent — no user prompt on success)

Run a single silent check. If Docker is running, proceed directly to Step 2 without any output.

```bash
docker info > /dev/null 2>&1 && echo "OK" || echo "FAIL"
```

- **Docker not running:** Use `AskUserQuestion`:
  - **question:** "Docker is required but not running. Please start Docker and let me know when it's ready."
  - **header:** "Docker"
  - **options:**
    - `Docker is running now` - I've started Docker
    - `Help me start Docker` - Show me how to start it
  - If user selects "Help me start Docker": macOS: `open -a Docker` / Linux: `sudo systemctl start docker`
  - Re-verify with `docker info` before proceeding.

Java and Maven are not checked upfront — missing or wrong versions produce clear errors at build time (Step 7).

### Step 2: Ask Edition and License Location

VoltDB requires a license file (Developer Edition uses a free license; Enterprise Edition requires a commercial license). Use `AskUserQuestion` with:
- **question:** "Which VoltDB edition do you want to use?"
- **header:** "Edition"
- **options:**
  - `Developer Edition` (Recommended) - Free license, no command logging (amd64 image — runs under emulation on Apple Silicon)
  - `Enterprise Edition` - Requires commercial Enterprise license

Then ask for the license file location using `AskUserQuestion` with:
- **question:** "Where is your VoltDB license file?"
- **header:** "License"
- **options:**
  - `VOLTDB_LICENSE env var` (Recommended) - I have VOLTDB_LICENSE environment variable set
  - `~/voltdb-license.xml` - License is in my home directory
  - `/tmp/voltdb-license.xml` - License is at /tmp
  - `Specify path` - I'll provide the path to my license file

After the user responds:
1. If `VOLTDB_LICENSE env var`: run `echo $VOLTDB_LICENSE` and verify the file exists at that path using `test -f "$VOLTDB_LICENSE"`.
2. If `~/voltdb-license.xml`: verify the file exists using `test -f ~/voltdb-license.xml`.
3. If `/tmp/voltdb-license.xml`: verify the file exists using `test -f /tmp/voltdb-license.xml`.
4. If `Specify path`: ask the user for the path, then verify the file exists.

**If the license file is not found at the specified location**, inform the user and ask them to correct the path. Do not proceed until a valid license file is confirmed.

Save the confirmed license path and edition choice — they will be used when generating `test.properties`.

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

**Phase 1 — Partitioning Analysis** (skip for Key-Value):
1. Read [rules/part-critical-rules.md](rules/part-critical-rules.md) and [rules/part-choose-column.md](rules/part-choose-column.md)
2. If co-location is needed, read [rules/part-colocation.md](rules/part-colocation.md)
3. If cross-domain queries exist, read [rules/part-lookup-tables.md](rules/part-lookup-tables.md)
4. Recommend partition column, co-location groups, lookup tables, and procedure types
5. **Validate replicated table candidates:** For each table marked as replicated, check whether any of the planned high-frequency operations (order placement, transaction processing, inventory updates, counter increments) will write to it. If yes, the table is not truly reference data — partition it instead. Only tables that are genuinely read-mostly (written rarely via admin/bulk operations) should be replicated.
6. Present strategy for user confirmation using `AskUserQuestion`:
   - **question:** "Does this partitioning strategy work for you? [strategy summary]"
   - **header:** "Strategy"
   - **options:**
     - `Yes, proceed` (Recommended)
     - `Modify strategy` - I want to change something
     - `Explain more` - Tell me more about the trade-offs

**Phase 1b — Multi-Step Transaction Analysis** (advanced — skip for Key-Value or simple CRUD):

After the user confirms the partitioning strategy, analyze the data model for multi-step atomic operation opportunities. Read [rules/ddl-multi-step-transactions.md](rules/ddl-multi-step-transactions.md) for patterns and detection rules.

Look for these patterns in the user's data model:
- Transfer/move operations between entities (e.g., funds transfer, inventory movement)
- Validate-then-write patterns (e.g., check balance before debit)
- Multi-table writes that should be atomic (e.g., create order + update inventory)
- Read-compute-write cycles (e.g., calculate discount then apply)
- Mutation + audit logging

If opportunities are detected, use `AskUserQuestion` with:
- **question:** "Your data model has opportunities for multi-step atomic operations. In VoltDB, a stored procedure is a full ACID transaction — multiple reads, business logic, and writes all execute atomically. Would you like to add any of these? [list detected opportunities]"
- **header:** "Transactions"
- **options:**
  - `Yes, add suggested transactions` (Recommended) - Generate the suggested multi-step procedures
  - `Let me choose` - I'll pick which ones I want
  - `Skip for now` - Keep it simple with basic CRUD only

If the user wants multi-step procedures, ensure partitioning alignment:
- All tables in the transaction must be co-located on the same partition column, or be replicated
- The procedure must be partitioned on the common partition column
- Replicated tables can be read but not written from single-partition procedures
- **Guardrail:** For each proposed multi-step procedure, check every write statement (INSERT/UPDATE/UPSERT/DELETE). If any write targets a replicated table, first reconsider whether that table should be partitioned instead (see Phase 1 step 5). If it must stay replicated, the procedure must be declared as multi-partition.

**Phase 2 — Code Generation:**
1. Read [rules/proj-setup.md](rules/proj-setup.md) → create Maven project structure + `pom.xml`
2. Read [rules/ddl-procedures.md](rules/ddl-procedures.md) → generate:
   - `src/main/resources/ddl.sql` (with `DROP PROCEDURE IF EXISTS` pattern) — simple single-statement procedures are defined inline in DDL using `CREATE PROCEDURE ... AS sql-statement`
   - **PARAMETER N check:** For each DDL-defined single-partition procedure, verify that the partition column's `?` is at position 0. If not (common for co-located table upserts where the table's own ID comes first), add `PARAMETER N`. See the verification section in ddl-procedures.md.
   - `src/main/resources/remove_db.sql` (DROP in dependency order)
   - Java class procedures under `src/main/java/[package]/procedures/` — **only** for co-located access (multiple SQL statements) and multi-step transactions
   - If multi-step transactions were requested (Phase 1b), also generate multi-step procedure classes using the pattern from [rules/ddl-multi-step-transactions.md](rules/ddl-multi-step-transactions.md)
3. Generate `[AppName]App.java` — main client app (rules/proj-setup.md template)
4. Generate `VoltDBSetup.java` — schema deployment (rules/proj-setup.md template)
5. Generate `CsvDataLoader.java` — CSV loading utility (rules/test-data-and-patterns.md template)
6. Generate CSV data files in `src/main/resources/data/` (rules/test-data-and-patterns.md)
7. Read [rules/test-base-class.md](rules/test-base-class.md) → generate `IntegrationTestBase.java`
8. Read [rules/test-data-and-patterns.md](rules/test-data-and-patterns.md) → generate `[TestName]IT.java`
9. Generate `test.properties` at `src/test/resources/test.properties` with testcontainer mode, shutdown enabled, the confirmed license path from Step 2, and the correct `voltdb.image.name`/`voltdb.image.version` for the chosen edition (Developer Edition: `voltactivedata/volt-developer-edition` / `14.1.0_voltdb`; Enterprise Edition: `voltdb/voltdb-enterprise` / `14.3.1`)
10. Read [rules/workflow-readme-template.md](rules/workflow-readme-template.md) → generate project `README.md`

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
