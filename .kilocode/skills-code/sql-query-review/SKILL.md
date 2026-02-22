---
name: sql-query-review
description: Reviews SQL queries for correctness, performance, and security before
  they reach production.
mode: code
license: MIT
---
# SQL Query Review Skill

## When to Use

Apply this skill when:
- The user shares a SQL query and asks for a review, feedback, or optimisation
- The user asks "is this query correct?", "why is this query slow?", or "is this safe?"
- A query is shown in context of a code review or migration
- The user asks to check a query for SQL injection risks

Do NOT apply when the user is asking to design a schema or write migrations.

## Correctness

### NULL Handling
```sql
-- BAD: NULL != 'active' returns NULL, not TRUE
WHERE status != 'active'

-- GOOD
WHERE status != 'active' OR status IS NULL
```

### JOIN Type
- Use `INNER JOIN` when both sides must exist
- Use `LEFT JOIN` when the right side is optional — check for accidental row multiplication
- Avoid `CROSS JOIN` unless the cartesian product is intentional

### Aggregation Traps
```sql
-- BAD: col_b is not in GROUP BY and not aggregated
SELECT col_a, col_b, COUNT(*) FROM t GROUP BY col_a;

-- GOOD
SELECT col_a, MAX(col_b), COUNT(*) FROM t GROUP BY col_a;
```

## Performance

### Avoid Functions on Indexed Columns
```sql
-- BAD: index on created_at is not used
WHERE DATE(created_at) = '2024-01-01'

-- GOOD: range scan uses the index
WHERE created_at >= '2024-01-01' AND created_at < '2024-01-02'
```

### Use EXISTS Instead of IN for Subqueries
```sql
-- BAD: IN with large subquery can be slow
WHERE id IN (SELECT user_id FROM orders WHERE total > 1000)

-- GOOD
WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id AND total > 1000)
```

### LIMIT on Large Tables
Always add `LIMIT` when testing queries manually on production data.

### Check Execution Plan
```sql
EXPLAIN ANALYZE SELECT ...;
```
Look for: `Seq Scan` on large tables (add index?), `Hash Join` on huge datasets, row estimates vs actual rows.

## Security

### No String Interpolation
```python
# BAD: SQL injection
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# GOOD: parameterised query
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_input,))
```

### Principle of Least Privilege
- Read-only queries → use a read-only DB user
- Never run application queries as `superuser`

## Checklist

- [ ] All columns in SELECT are intentional (avoid `SELECT *` in production)
- [ ] JOINs use indexed columns
- [ ] WHERE clause is selective (filters applied early)
- [ ] No functions wrapping indexed columns
- [ ] Parameterised queries used (no string interpolation)
- [ ] Query tested with `EXPLAIN ANALYZE` on realistic data volume
- [ ] Transactions used for multi-statement writes