# Multi-Step Atomic Transactions

> **Category:** DDL & Stored Procedures | **Impact:** HIGH | **Level:** Advanced

## Context

VoltDB stored procedures are fully ACID — all SQL statements within a single procedure call either ALL commit or ALL rollback. This makes stored procedures the natural place for multi-step atomic operations that would require explicit transaction management in other databases.

A multi-step stored procedure can:
- Read from multiple tables, apply business logic in Java, then write to multiple tables — all atomically
- Validate preconditions before making changes (no partial updates if validation fails)
- Execute batches of SQL statements efficiently using `voltQueueSQL()` + `voltExecuteSQL()`

This is an **advanced** capability. Simple CRUD applications don't need it. Offer it when the user's data model suggests operations that must be atomic across multiple tables or involve read-then-write patterns with business logic.

## When to Suggest Multi-Step Transactions

Analyze the user's data model for these patterns:

| Pattern | Example | Suggestion |
|---------|---------|------------|
| **Transfer/move** between entities | Transfer funds between accounts, move inventory between warehouses | "Would you like an atomic transfer procedure that debits one and credits another in a single transaction?" |
| **Validate-then-write** | Check stock before placing order, verify balance before payment | "Would you like a procedure that validates conditions before writing, rejecting the operation atomically if validation fails?" |
| **Write to multiple co-located tables** | Create order + order items + update inventory | "Would you like to group these related writes into a single atomic procedure?" |
| **Read-compute-write** | Calculate discount based on history, then apply it | "Would you like a procedure that reads current state, applies business logic, and writes results atomically?" |
| **Audit/log alongside mutation** | Update record + insert audit log entry | "Would you like writes and their audit trail recorded in a single atomic operation?" |

**How to prompt the user:**

After presenting the partitioning strategy (Step 6 Phase 1), if multi-step opportunities are detected, ask:

> "Your data model has opportunities for multi-step atomic operations. VoltDB stored procedures are fully ACID — multiple reads, business logic, and writes all execute as one atomic transaction. Would you like to create any of these?"

Then list the specific suggestions based on the detected patterns.

## Partitioning Alignment Rules

Multi-step transactions work best as **single-partition** procedures. For this to work:

1. **All tables accessed must be co-located** on the same partition column value, OR be replicated tables
2. **The procedure is partitioned** on the common partition column
3. **Replicated tables can be read** from any single-partition procedure (they're copied to all partitions)
4. **Replicated tables cannot be written** from single-partition procedures — writes to replicated tables require multi-partition procedures

**Verification checkpoint — apply before generating each multi-step procedure:**

For every UPDATE/INSERT/UPSERT/DELETE statement in the procedure, check the target table:
- Is it co-located on the procedure's partition column? → OK for single-partition
- Is it a replicated table? → **STOP.** Single-partition procedures cannot write to replicated tables.
  - First, reconsider: should this table really be replicated? If the procedure writes to it on every transaction (e.g., decrementing stock, updating counters), the table is not truly reference data — **partition it instead**.
  - If the table must remain replicated and writes are rare, make the procedure **multi-partition**.

```
✓ Single-partition multi-step (FAST — all on same partition):
  ACCOUNTS partitioned on ACCOUNT_ID
  TRANSACTIONS partitioned on ACCOUNT_ID (co-located)
  MERCHANTS replicated (read-only from any partition)
  → Procedure partitioned on ACCOUNT_ID can:
    - READ from ACCOUNTS, TRANSACTIONS, MERCHANTS
    - WRITE to ACCOUNTS and TRANSACTIONS
    - All in one atomic operation

✗ WRONG — single-partition procedure writing to replicated table:
  ORDERS partitioned on CUSTOMER_ID
  PRODUCTS replicated
  PlaceOrder partitioned on CUSTOMER_ID tries to UPDATE PRODUCTS
  → DDL load FAILS: "Trying to write to replicated table in single-partition procedure"
  → Fix: If PRODUCTS.STOCK is updated frequently, partition PRODUCTS on PRODUCT_ID
    and make PlaceOrder a multi-partition procedure.

✗ Cannot do in single-partition:
  ACCOUNTS partitioned on ACCOUNT_ID
  PRODUCTS partitioned on PRODUCT_ID (different partition key!)
  → Must use multi-partition procedure (slower) or lookup table
```

**Cross-partition transfers** (e.g., transfer between two accounts on different partitions) require multi-partition procedures. These are slower but still fully ACID.

## Stored Procedure Pattern: Multi-Step Atomic

The key techniques:
- **Batch SQL statements** with `voltQueueSQL()` — queue multiple statements, execute as a batch
- **Multiple execution rounds** with `voltExecuteSQL()` — read results, apply logic, queue more statements
- **Final commit** with `voltExecuteSQL(true)` — the `true` parameter commits the transaction
- **Early return** to abort — returning before `voltExecuteSQL(true)` rolls back all changes

```java
package [package].procedures;

import org.voltdb.SQLStmt;
import org.voltdb.VoltProcedure;
import org.voltdb.VoltTable;
import org.voltdb.VoltType;

/**
 * Multi-step atomic procedure example.
 * All steps execute as a single ACID transaction.
 *
 * Steps:
 * 1. Validate preconditions (SELECT)
 * 2. Apply business logic in Java
 * 3. Write changes (INSERT/UPDATE) and commit atomically
 */
public class [ProcedureName] extends VoltProcedure {

    // --- SQL Statements ---

    // Phase 1: Validation queries
    public final SQLStmt checkPrimary = new SQLStmt(
        "SELECT [COLUMNS] FROM [PRIMARY_TABLE] WHERE [PARTITION_COL] = ?;");

    public final SQLStmt checkRelated = new SQLStmt(
        "SELECT [COLUMNS] FROM [RELATED_TABLE] WHERE [PARTITION_COL] = ?;");

    // Optionally read from a replicated lookup table
    public final SQLStmt checkLookup = new SQLStmt(
        "SELECT [COLUMNS] FROM [REPLICATED_TABLE] WHERE [LOOKUP_COL] = ?;");

    // Phase 2: Write operations
    public final SQLStmt updatePrimary = new SQLStmt(
        "UPDATE [PRIMARY_TABLE] SET [COLUMN] = ? WHERE [PARTITION_COL] = ?;");

    public final SQLStmt insertRelated = new SQLStmt(
        "INSERT INTO [RELATED_TABLE] ([COLUMNS]) VALUES (?, ?, ...);");

    // --- Result builder for status reporting ---

    private VoltTable buildResult(byte success, String message) {
        VoltTable result = new VoltTable(
            new VoltTable.ColumnInfo("SUCCESS", VoltType.TINYINT),
            new VoltTable.ColumnInfo("MESSAGE", VoltType.STRING)
        );
        result.addRow(success, message);
        return result;
    }

    // --- Main procedure logic ---

    // Partition key position must match DDL PARAMETER N (default: parameter 0)
    public VoltTable run([partition_key_type] partitionKey, [other parameters...]) {

        // ==========================================
        // Phase 1: Validate preconditions
        // ==========================================
        // Queue multiple SELECT statements and execute as a batch
        voltQueueSQL(checkPrimary, EXPECT_ZERO_OR_ONE_ROW, partitionKey);
        voltQueueSQL(checkRelated, partitionKey);
        // Can also read from replicated tables:
        // voltQueueSQL(checkLookup, lookupId);
        VoltTable[] checks = voltExecuteSQL();

        // Validate results — early return aborts (rolls back) the transaction
        VoltTable primaryInfo = checks[0];
        if (primaryInfo.getRowCount() == 0) {
            return buildResult((byte) 0, "Primary record not found");
        }

        primaryInfo.advanceRow();
        // Extract values for business logic
        // long someValue = primaryInfo.getLong("COLUMN_NAME");

        // ==========================================
        // Phase 2: Apply business logic in Java
        // ==========================================
        // Compute derived values, check limits, apply rules
        // This logic executes between SQL rounds — fully atomic

        // Example: check a business rule
        // if (someValue + amount > limit) {
        //     return buildResult((byte) 0, "Exceeds limit");
        // }

        // ==========================================
        // Phase 3: Write changes and commit
        // ==========================================
        voltQueueSQL(updatePrimary, newValue, partitionKey);
        voltQueueSQL(insertRelated, relatedId, partitionKey, ...);
        voltExecuteSQL(true);  // true = COMMIT the transaction

        return buildResult((byte) 1, "Success");
    }
}
```

## DDL Declaration for Multi-Step Procedures

```sql
-- Multi-step procedures are declared the same way as any single-partition procedure.
-- The PARAMETER clause specifies which run() parameter is the partition key (0-indexed).
DROP PROCEDURE [package].procedures.[ProcedureName] IF EXISTS;
CREATE PROCEDURE PARTITION ON TABLE [PRIMARY_TABLE] COLUMN [PARTITION_COL]
    FROM CLASS [package].procedures.[ProcedureName];

-- If partition key is NOT the first parameter, specify its position:
-- CREATE PROCEDURE PARTITION ON TABLE [PRIMARY_TABLE] COLUMN [PARTITION_COL] PARAMETER [N]
--     FROM CLASS [package].procedures.[ProcedureName];
```

## Client Code Pattern

Multi-step procedures are called exactly like any other procedure. The client doesn't know or care that multiple steps happen inside:

```java
// In [AppName]App.java — call it like any single-partition procedure
public VoltTable process[Operation](long partitionKey, [other params...]) throws Exception {
    return client.callProcedureAsync("[ProcedureName]", partitionKey, [other params...])
        .thenApply(response -> checkResponse("[ProcedureName]", response).getResults()[0])
        .get();
}
```

## Integration Test Pattern

```java
@Test
void testMultiStepAtomicOperation() throws Exception {
    // Setup: insert prerequisite data
    app.upsert[Primary](partitionKey, ...);

    // Execute the multi-step procedure
    VoltTable result = app.process[Operation](partitionKey, ...);

    // Verify the result status
    assertTrue(result.advanceRow());
    assertEquals(1, result.getLong("SUCCESS"));

    // Verify all side effects happened atomically:
    // 1. Primary table was updated
    VoltTable primary = app.get[Primary](partitionKey);
    assertTrue(primary.advanceRow());
    assertEquals(expectedValue, primary.getLong("COLUMN"));

    // 2. Related record was inserted
    VoltTable[] related = app.get[Primary]With[Related](partitionKey);
    assertEquals(expectedCount, related[1].getRowCount());
}

@Test
void testMultiStepRejection() throws Exception {
    // Setup: create conditions that should cause rejection
    app.upsert[Primary](partitionKey, ...);

    // Execute — should be rejected by business logic
    VoltTable result = app.process[Operation](partitionKey, invalidParams...);

    // Verify rejection
    assertTrue(result.advanceRow());
    assertEquals(0, result.getLong("SUCCESS"));

    // Verify NO side effects (transaction was rolled back):
    VoltTable primary = app.get[Primary](partitionKey);
    assertTrue(primary.advanceRow());
    assertEquals(originalValue, primary.getLong("COLUMN"));
    // No related records should have been created
}
```

## Real-World Example: Fraud Detection Transaction Processing

This example from a fraud detection system shows a multi-step procedure that validates an account, checks fraud rules using materialized views, and either accepts or rejects a transaction — all atomically:

```java
public class ProcessTransaction extends VoltProcedure {

    // Phase 1: Validation queries
    public final SQLStmt checkAccount = new SQLStmt(
        "SELECT ENABLED, CAST(BALANCE AS FLOAT), CAST(DAILY_LIMIT AS FLOAT) " +
        "FROM ACCOUNTS WHERE ACCOUNT_ID = ?;");

    public final SQLStmt checkMerchant = new SQLStmt(
        "SELECT MERCHANT_ID FROM MERCHANTS WHERE MERCHANT_ID = ?;");

    // Phase 2: Fraud rule queries (using materialized views)
    public final SQLStmt checkTxn5Min = new SQLStmt(
        "SELECT TXN_COUNT, TOTAL_SPENT FROM TXN_SUMMARY_5MIN WHERE ACCOUNT_ID = ?;");

    public final SQLStmt checkTxn1Min = new SQLStmt(
        "SELECT TXN_COUNT, TOTAL_SPENT FROM TXN_SUMMARY_1MIN WHERE ACCOUNT_ID = ?;");

    // Phase 3: Write operations
    public final SQLStmt updateBalance = new SQLStmt(
        "UPDATE ACCOUNTS SET BALANCE = BALANCE + ? WHERE ACCOUNT_ID = ?;");

    public final SQLStmt insertTxn = new SQLStmt(
        "INSERT INTO TRANSACTIONS (TXN_ID, ACCOUNT_ID, TXN_TIME, MERCHANT_ID, " +
        "AMOUNT, DEVICE_ID, ACCEPTED, REASON) VALUES (?, ?, ?, ?, ?, ?, ?, ?);");

    public VoltTable run(long accountId, long txnId, long txnTimeMs,
                         int merchantId, double amount, String deviceId) {

        // Phase 1: Validate account and merchant (batch read)
        voltQueueSQL(checkAccount, EXPECT_ZERO_OR_ONE_ROW, accountId);
        voltQueueSQL(checkMerchant, EXPECT_ZERO_OR_ONE_ROW, merchantId);
        VoltTable[] checks = voltExecuteSQL();

        if (checks[0].getRowCount() == 0) {
            return buildResult((byte) 0, "Invalid Account");
        }
        checks[0].advanceRow();
        double balance = checks[0].getDouble(1);
        double dailyLimit = checks[0].getDouble(2);

        // Phase 2: Business logic — check limits and fraud rules
        if (amount > 5000) {
            return buildResult((byte) 0, "Large Transaction");
        }
        if (balance + amount > dailyLimit) {
            return buildResult((byte) 0, "Exceeds Daily Limit");
        }

        // Phase 2b: Check fraud rules via materialized views
        voltQueueSQL(checkTxn5Min, accountId);
        voltQueueSQL(checkTxn1Min, accountId);
        VoltTable[] fraudChecks = voltExecuteSQL();
        // ... evaluate fraud rules ...

        // Phase 3: Accept — update balance and record transaction atomically
        voltQueueSQL(updateBalance, amount, accountId);
        voltQueueSQL(insertTxn, txnId, accountId, txnTime, merchantId,
                     amount, deviceId, (byte) 1, "Accepted");
        voltExecuteSQL(true);  // COMMIT

        return buildResult((byte) 1, "Accepted");
    }
}
```

Key points from this example:
- **3 execution rounds:** validation reads → fraud rule reads → writes + commit
- **Java logic between rounds:** business rules evaluated between SQL batches
- **Early return = rollback:** if validation fails, the procedure returns before any writes
- **Replicated table access:** MERCHANTS is replicated, readable from any partition
- **Co-located tables:** ACCOUNTS and TRANSACTIONS share ACCOUNT_ID partition, so both are accessible
- **Final `voltExecuteSQL(true)`** commits all changes atomically
