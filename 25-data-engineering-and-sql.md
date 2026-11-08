# 25. Data Engineering & SQL

Almost every ML, data science and AI engineer loop has a SQL round or data pipeline questions. Models are only as good as the data pipelines feeding them.

### Contents
1. [Data modeling](#1-data-modeling)
2. [Storage: warehouse, lake, lakehouse](#2-storage-warehouse-lake-lakehouse)
3. [File and table formats](#3-file-and-table-formats)
4. [Pipelines: batch, streaming, ETL vs ELT](#4-pipelines-batch-streaming-etl-vs-elt)
5. [Orchestration, CDC, partitioning, data quality](#5-orchestration-cdc-partitioning-data-quality)
6. [Spark essentials](#6-spark-essentials)
7. [SQL interview: concepts](#7-sql-interview-concepts)
8. [SQL interview: 24 practice questions](#8-sql-interview-24-practice-questions)
9. [What-if scenarios (data engineering)](#9-what-if-scenarios-data-engineering)

---

## 1. Data modeling

**Q: OLTP vs OLAP?**
| | OLTP | OLAP |
|---|---|---|
| Purpose | Run the app (orders, users) | Analytics, reporting, ML training data |
| Queries | Many small reads/writes by key | Few large scans and aggregations |
| Design | Normalized (3NF), row storage | Denormalized (star schema), columnar storage |
| Examples | Postgres, MySQL | BigQuery, Snowflake, Redshift, Databricks |

**Q: Normalization vs denormalization?** Normalization removes duplication (less storage, easy updates, more joins). Denormalization duplicates data for faster reads (analytics, NoSQL).

**Q: Star schema?** One **fact table** (events/measurements: `fact_orders(order_id, date_key, customer_key, product_key, amount)`) in the middle, surrounded by **dimension tables** (descriptions: `dim_customer`, `dim_product`, `dim_date`). Simple joins, fast aggregations.
**Snowflake schema:** dimensions are normalized further (`dim_product → dim_category`). Less duplication, more joins.

```
              dim_date
                 │
dim_customer ── fact_orders ── dim_product
                 │
              dim_store
```

**Q: Fact table grain?** The meaning of one row ("one row per order line"). Always define grain first. A wrong grain causes double counting.

**Q: Slowly Changing Dimensions (SCD)?** How to handle dimension values that change (customer moves city).
| Type | How | History? |
|---|---|---|
| SCD 0 | Never change | n/a |
| SCD 1 | Overwrite old value | No |
| SCD 2 | New row with `valid_from`, `valid_to`, `is_current` | **Yes (most asked)** |
| SCD 3 | Extra column `previous_city` | Only last change |

**Why ML engineers care:** SCD2 gives **point-in-time correct** features (what the customer's city was *at the time* of the order) → no leakage.

## 2. Storage: warehouse, lake, lakehouse
| | Data warehouse | Data lake | Lakehouse |
|---|---|---|---|
| Data | Structured, cleaned | Any: raw files, images, logs | Any, with table features on top |
| Schema | On write | On read | Both |
| Cost | Higher | Cheap (object storage) | Cheap storage + compute |
| Examples | Snowflake, BigQuery, Redshift | S3/GCS/ADLS + files | Databricks (Delta), Iceberg/Hudi tables |
| Good for | BI, SQL analytics | ML raw data, archives | Both BI and ML on one copy |

**Medallion architecture:** **bronze** (raw, as ingested) → **silver** (cleaned, deduped, joined) → **gold** (business-level aggregates, features).

## 3. File and table formats
| Format | Type | Use |
|---|---|---|
| CSV / JSON | Row, text | Exchange, small data; slow, no types |
| **Parquet** | Columnar, compressed | Analytics/ML: read only needed columns, predicate pushdown |
| ORC | Columnar | Hive ecosystem |
| **Avro** | Row, schema embedded | Streaming/Kafka messages, schema evolution |
| **Delta Lake / Apache Iceberg / Hudi** | Table format over Parquet | ACID transactions, time travel, schema evolution, upserts (MERGE) on data lakes |

**Q: Why columnar for analytics?** Queries read few columns of many rows → read less data; same-type values compress well.

## 4. Pipelines: batch, streaming, ETL vs ELT
- **Batch:** process data in chunks on a schedule (hourly/daily). Simple, cheap, high latency. Spark, dbt, SQL.
- **Streaming:** process events continuously (seconds). Kafka + Flink / Spark Structured Streaming / Kafka Streams. Needed for fraud, real-time features, live dashboards.
- **Lambda architecture:** batch layer (accurate) + speed layer (fast) merged. **Kappa:** stream only, reprocess by replaying the log.
- **ETL:** transform before loading into the warehouse. **ELT:** load raw first, transform inside the warehouse with SQL (dbt). ELT is the modern default (cheap storage, fast warehouses).

**Streaming concepts to name:**
- **Event time vs processing time:** when it happened vs when we saw it.
- **Windows:** tumbling (fixed, non-overlapping), sliding (overlapping), session (gap-based).
- **Watermarks:** how long to wait for late events before closing a window.
- **Exactly-once:** checkpoints + idempotent/transactional sinks.

## 5. Orchestration, CDC, partitioning, data quality
- **Orchestration:** Airflow, Dagster, Prefect. They run DAGs of tasks, retries, schedules, backfills, dependencies, SLAs.
- **Idempotent pipelines:** re-running a day gives the same result (overwrite partition `date=2026-11-01`, or MERGE by key). You need this for retries and backfills.
- **CDC (Change Data Capture):** read the database's change log (e.g., Debezium on Postgres WAL/MySQL binlog) → Kafka → lake/warehouse. Near-real-time copies without heavy queries on production DB.
- **Partitioning:** split tables by a column (usually date) so queries skip data. **Clustering / bucketing / Z-ordering:** sort data inside partitions for faster filters. Avoid over-partitioning (tiny files).
- **Data quality checks:** freshness, row counts, nulls, uniqueness, accepted values, referential integrity, distribution checks. Tools: dbt tests, Great Expectations, Soda. **Data contracts** with producers.
- **Lineage & catalog:** know where data comes from and who uses it (DataHub, Unity Catalog, OpenLineage).

## 6. Spark essentials
- **Driver** plans, **executors** run tasks on **partitions**. Transformations are **lazy**; actions trigger execution.
- **Narrow** transformations (map, filter) don't move data. **Wide** ones (groupBy, join) cause a **shuffle** across the network, which is expensive.
- **Joins:** **broadcast join** when one side is small (send it to every executor, no shuffle); sort-merge join for two big tables.
- **Data skew:** one key has most rows → one task runs forever. Fixes: salting the key, broadcast join, AQE (adaptive query execution) skew handling.
- `cache()/persist()` reused DataFrames; avoid `collect()` on big data; prefer built-in functions over Python UDFs.
- **Repartition vs coalesce:** repartition shuffles to any number; coalesce only reduces partitions without full shuffle.

---

## 7. SQL interview: concepts

**Q: Order of execution of a SQL query?** `FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT`. That's why you can't use a SELECT alias in WHERE.

**Q: WHERE vs HAVING?** WHERE filters rows before grouping; HAVING filters groups after aggregation.

**Q: Join types?** INNER (matches only), LEFT (all left rows + matches, NULL otherwise), RIGHT, FULL OUTER, CROSS (every combination), SELF join (table with itself), anti-join (`LEFT JOIN ... WHERE right.id IS NULL` or `NOT EXISTS`), semi-join (`EXISTS`).

**Q: UNION vs UNION ALL?** UNION removes duplicates (slower); UNION ALL keeps all.

**Q: ROW_NUMBER vs RANK vs DENSE_RANK?** For scores 100, 90, 90, 80: ROW_NUMBER 1,2,3,4; RANK 1,2,2,4; DENSE_RANK 1,2,2,3.

**Q: COUNT(*) vs COUNT(col)?** COUNT(*) counts rows; COUNT(col) skips NULLs.

**Q: NULL gotchas?** `NULL = NULL` is not true → use `IS NULL`. `NOT IN (subquery with NULL)` returns no rows → use `NOT EXISTS`. Aggregates ignore NULLs.

**Q: When does an index help?** Selective filters, joins, ORDER BY on indexed columns. Doesn't help with functions on the column (`WHERE YEAR(created_at)=2026` → rewrite as a range), leading wildcards (`LIKE '%abc'`), or low-selectivity columns.

**Q: CTE vs subquery?** A CTE (`WITH x AS (...)`) has the same power, reads better, and can be recursive.

**Q: Window function?** Computes over a set of rows related to the current row **without collapsing rows**: `SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at)`.

---

## 8. SQL interview: 24 practice questions

Tables used:
```
users(user_id, signup_date, country)
orders(order_id, user_id, order_date, amount, status)
events(user_id, event_time, event_name)          -- e.g. 'view', 'add_to_cart', 'purchase'
employees(emp_id, name, dept_id, salary, manager_id)
departments(dept_id, dept_name)
logins(user_id, login_date)
```
(Syntax is standard/Postgres-style; small differences across databases.)

**1. Second highest salary.**
```sql
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
-- or: SELECT DISTINCT salary FROM employees ORDER BY salary DESC LIMIT 1 OFFSET 1;
```

**2. N-th highest salary (generic).**
```sql
SELECT salary FROM (
  SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk FROM employees
) t WHERE rnk = 3 LIMIT 1;
```

**3. Top 3 earners per department (top-N per group).**
```sql
SELECT dept_id, name, salary FROM (
  SELECT e.*, DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk
  FROM employees e
) t WHERE rnk <= 3;
```

**4. Employees earning more than their manager (self join).**
```sql
SELECT e.name
FROM employees e JOIN employees m ON e.manager_id = m.emp_id
WHERE e.salary > m.salary;
```

**5. Departments with no employees (anti-join).**
```sql
SELECT d.dept_name FROM departments d
LEFT JOIN employees e ON e.dept_id = d.dept_id
WHERE e.emp_id IS NULL;
```

**6. Users who never ordered.**
```sql
SELECT u.user_id FROM users u
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.user_id);
```

**7. Find duplicate rows.**
```sql
SELECT user_id, order_date, amount, COUNT(*) AS cnt
FROM orders GROUP BY user_id, order_date, amount
HAVING COUNT(*) > 1;
```

**8. Delete duplicates, keep the first (dedupe).**
```sql
DELETE FROM orders WHERE order_id IN (
  SELECT order_id FROM (
    SELECT order_id, ROW_NUMBER() OVER (
      PARTITION BY user_id, order_date, amount ORDER BY order_id) AS rn
    FROM orders) t
  WHERE rn > 1);
```

**9. Latest order per user.**
```sql
SELECT * FROM (
  SELECT o.*, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC) AS rn
  FROM orders o) t
WHERE rn = 1;
```

**10. Running total of revenue by day.**
```sql
SELECT order_date, daily_rev,
       SUM(daily_rev) OVER (ORDER BY order_date) AS running_total
FROM (SELECT order_date, SUM(amount) AS daily_rev FROM orders GROUP BY order_date) d;
```

**11. 7-day moving average of revenue.**
```sql
SELECT order_date,
       AVG(daily_rev) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma7
FROM (SELECT order_date, SUM(amount) AS daily_rev FROM orders GROUP BY order_date) d;
-- note: assumes one row per day; fill missing days with a calendar table for exact results
```

**12. Month-over-month growth %.**
```sql
WITH m AS (
  SELECT DATE_TRUNC('month', order_date) AS month, SUM(amount) AS rev
  FROM orders GROUP BY 1)
SELECT month, rev,
       ROUND(100.0 * (rev - LAG(rev) OVER (ORDER BY month)) / LAG(rev) OVER (ORDER BY month), 2) AS mom_pct
FROM m;
```

**13. Percentage of total per country.**
```sql
SELECT u.country, SUM(o.amount) AS rev,
       100.0 * SUM(o.amount) / SUM(SUM(o.amount)) OVER () AS pct_of_total
FROM orders o JOIN users u USING (user_id)
GROUP BY u.country;
```

**14. Median order amount.**
```sql
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median FROM orders;
-- Without PERCENTILE_CONT:
SELECT AVG(amount) FROM (
  SELECT amount, ROW_NUMBER() OVER (ORDER BY amount) AS rn, COUNT(*) OVER () AS n FROM orders) t
WHERE rn IN ((n + 1) / 2, (n + 2) / 2);
```

**15. Day-1 retention (users who came back the day after signup).**
```sql
SELECT COUNT(DISTINCT l.user_id) * 1.0 / COUNT(DISTINCT u.user_id) AS d1_retention
FROM users u
LEFT JOIN logins l ON l.user_id = u.user_id AND l.login_date = u.signup_date + INTERVAL '1 day';
```

**16. Monthly cohort retention table.**
```sql
WITH cohort AS (
  SELECT user_id, DATE_TRUNC('month', signup_date) AS cohort_month FROM users),
activity AS (
  SELECT DISTINCT user_id, DATE_TRUNC('month', login_date) AS active_month FROM logins)
SELECT c.cohort_month,
       (EXTRACT(YEAR FROM a.active_month) - EXTRACT(YEAR FROM c.cohort_month)) * 12
       + EXTRACT(MONTH FROM a.active_month) - EXTRACT(MONTH FROM c.cohort_month) AS month_number,
       COUNT(DISTINCT a.user_id) AS active_users
FROM cohort c JOIN activity a USING (user_id)
GROUP BY 1, 2 ORDER BY 1, 2;
```

**17. Conversion funnel (view → add_to_cart → purchase).**
```sql
SELECT
  COUNT(DISTINCT CASE WHEN event_name = 'view' THEN user_id END)        AS viewed,
  COUNT(DISTINCT CASE WHEN event_name = 'add_to_cart' THEN user_id END) AS added,
  COUNT(DISTINCT CASE WHEN event_name = 'purchase' THEN user_id END)    AS purchased
FROM events
WHERE event_time >= DATE '2026-11-01';
-- Strict funnel (steps in order) → compare MIN(event_time) per step per user.
```

**18. Users who logged in 3+ consecutive days (gaps and islands).**
```sql
WITH d AS (
  SELECT DISTINCT user_id, login_date FROM logins),
g AS (
  SELECT user_id, login_date,
         login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date))::int AS grp
  FROM d)
SELECT user_id, MIN(login_date) AS streak_start, COUNT(*) AS streak_len
FROM g GROUP BY user_id, grp
HAVING COUNT(*) >= 3;
-- Trick: date minus row number is constant within a consecutive streak.
```

**19. Sessionize events (new session after 30 min of inactivity).**
```sql
WITH e AS (
  SELECT user_id, event_time,
         CASE WHEN event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time)
                   > INTERVAL '30 minutes'
                OR LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) IS NULL
              THEN 1 ELSE 0 END AS new_session
  FROM events)
SELECT user_id, event_time,
       SUM(new_session) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
FROM e;
```

**20. Time between a user's consecutive orders.**
```sql
SELECT user_id, order_date,
       order_date - LAG(order_date) OVER (PARTITION BY user_id ORDER BY order_date) AS days_since_prev
FROM orders;
```

**21. Users whose first order was over 100.**
```sql
SELECT user_id FROM (
  SELECT user_id, amount, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date, order_id) AS rn
  FROM orders) t
WHERE rn = 1 AND amount > 100;
```

**22. Pivot: revenue per status as columns.**
```sql
SELECT order_date,
       SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) AS completed,
       SUM(CASE WHEN status = 'refunded'  THEN amount ELSE 0 END) AS refunded
FROM orders GROUP BY order_date;
```

**23. Daily active users (DAU) and 7-day rolling distinct users.**
```sql
SELECT login_date, COUNT(DISTINCT user_id) AS dau FROM logins GROUP BY login_date;

SELECT d.login_date, COUNT(DISTINCT l.user_id) AS wau_rolling
FROM (SELECT DISTINCT login_date FROM logins) d
JOIN logins l ON l.login_date BETWEEN d.login_date - INTERVAL '6 days' AND d.login_date
GROUP BY d.login_date;
-- (COUNT DISTINCT is not allowed as a window function in most databases → self-join)
```

**24. Recursive CTE: all reports under a manager (org chart).**
```sql
WITH RECURSIVE reports AS (
  SELECT emp_id, name, manager_id, 1 AS level FROM employees WHERE emp_id = 1
  UNION ALL
  SELECT e.emp_id, e.name, e.manager_id, r.level + 1
  FROM employees e JOIN reports r ON e.manager_id = r.emp_id)
SELECT * FROM reports;
```

**How to answer SQL questions in interviews:** restate the output (columns, one row per what?), ask about duplicates/NULLs/ties, build step by step with CTEs, then mention performance (indexes, partitions).

---

## 9. What-if scenarios (data engineering)

### The daily pipeline is late and the 9 AM dashboard/model is stale
**Causes (ranked):** upstream source late; data volume spike; resource contention (shared cluster); a slow step (skew, bad join); failed task stuck in retries.
**Isolate:** look at task timeline in the orchestrator. Which task got slower? Compare input size vs normal.
**Fix now:** rerun the failed part, add resources, publish yesterday's data with a "stale" banner. **Long-term:** SLA alerts on upstream freshness, sensors waiting for data, optimize the slow step, separate compute for critical pipelines.
**Prevent:** freshness SLOs + alerts *before* consumers notice.

### Duplicate rows appeared in a table
**Causes:** at-least-once delivery from Kafka; pipeline re-ran and appended instead of overwriting; join fan-out (joining on a non-unique key); source sent the same records twice.
**Isolate:** check counts by key and by load batch; check whether duplicates share the same `ingested_at`.
**Fix:** make loads idempotent (overwrite partition or `MERGE` on business key), dedupe with `ROW_NUMBER()`, fix join keys.
**Prevent:** uniqueness tests on primary keys in every run.

### A query that took 10 seconds now takes 10 minutes
**Causes:** data grew; missing partition filter (full scan); stats out of date → bad plan; new join causing explosion; skew; lock contention (OLTP).
**Isolate:** `EXPLAIN / EXPLAIN ANALYZE`; check bytes scanned; compare plans.
**Fix:** add partition filter/index, rewrite (filter early, avoid functions on indexed columns, avoid `SELECT *`), update statistics, pre-aggregate into a summary table.

### Upstream team changed a column's type / renamed a column
**Fix now:** pin to the previous schema version or map the column, backfill. **Long-term:** **data contracts** + schema registry + CI checks that fail producer changes that break consumers; schema evolution rules (add columns, never rename/remove without notice).

### You need to backfill 2 years of data with new logic
**Plan:** idempotent job parameterized by date; run in chunks (per month), in parallel within limits; write to a new table/version, validate against old, then swap; don't overload production sources (read from snapshots/replicas); track progress.

### A Spark join runs forever at 99% (one task stuck)
**Cause:** **data skew**. One key (e.g., `user_id = NULL` or a huge customer) has most rows.
**Fix:** filter/handle NULL keys separately, **salt** the skewed key, broadcast the small table, enable AQE skew join.

### The data lake has millions of tiny files, queries are slow
**Cause:** streaming writes or over-partitioning produce small files → overhead per file.
**Fix:** compaction jobs (`OPTIMIZE` in Delta, rewrite in Iceberg), larger write batches, fewer partitions, auto-compaction.

### Numbers in the dashboard don't match the finance report
**Isolate:** compare definitions (gross vs net, time zone, refunds included?, dedupe rules), compare at the lowest grain for one day.
**Fix:** one shared **metrics layer / semantic layer** with agreed definitions, documented.

### Training data has future information (leakage) from a pipeline
**Cause:** joined latest dimension values instead of values at event time.
**Fix:** SCD2 dimensions + point-in-time joins (feature store). See [07](07-ml-fundamentals.md#8-data-preparation--feature-engineering).

### Streaming job shows wrong counts because events arrive late
**Fix:** use event time with watermarks, allow late data updates, and correct with a daily batch reconciliation.
