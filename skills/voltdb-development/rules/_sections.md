# Rule Sections

Defines the category order used by `scripts/build.sh` to compile `AGENTS.md`.

| Priority | Prefix | Category | Impact |
|----------|--------|----------|--------|
| 1 | `part-` | Partitioning Strategy | HIGH |
| 2 | `ddl-` | DDL & Stored Procedures | HIGH |
| 2a | `ddl-multi-step-` | Multi-Step Atomic Transactions (Advanced) | HIGH |
| 3 | `proj-` | Project Setup | MEDIUM |
| 4 | `test-` | Integration Testing | MEDIUM |
| 5 | `workflow-` | Workflow & Templates | MEDIUM |
