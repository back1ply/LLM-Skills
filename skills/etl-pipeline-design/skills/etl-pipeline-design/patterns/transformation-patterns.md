# Data Transformation Patterns Reference

## Transformation Patterns

### 1. Enrichment

**Purpose**: Enhance data with additional sources

```sql
-- Enrich orders with human-readable status
SELECT 
  o.order_id,
  o.amount,
  s.status_name  -- From lookup table
FROM orders o
JOIN status_codes s ON o.status_code = s.code
```

---

### 2. Joining

**Purpose**: Combine datasets on common keys

```sql
-- Add user country to sales data
SELECT 
  s.*,
  u.country
FROM sales s
JOIN users u ON s.user_id = u.id
```

**Join Types**:

- `INNER JOIN`: Only matching rows
- `LEFT JOIN`: All from left + matches from right
- `FULL OUTER JOIN`: All rows from both sides

---

### 3. Filtering

**Purpose**: Select only necessary records

```sql
-- Remove data before 2025
SELECT * FROM purchases
WHERE date >= '2025-01-01'
```

---

### 4. Structuring

**Purpose**: Convert between formats

```python
# JSON to tabular (PySpark)
from pyspark.sql.functions import from_json, col

df = spark.read.json("s3://bucket/raw_data.json")
df.write.format("delta").save("/delta/structured_data")
```

---

### 5. Conversion

**Purpose**: Change data types

```sql
-- String to timestamp
SELECT 
  CAST(created_at AS TIMESTAMP) as created_timestamp,
  -- Unix timestamp conversion
  FROM_UNIXTIME(unix_ts) as readable_time
FROM events
```

---

### 6. Aggregation

**Purpose**: Summarize data

```sql
-- Aggregate IoT sensor data from milliseconds to seconds
SELECT 
  DATE_TRUNC('second', event_time) as event_second,
  sensor_id,
  AVG(reading) as avg_reading,
  COUNT(*) as num_readings
FROM sensor_data
GROUP BY 1, 2
```

---

### 7. Anonymization

**Purpose**: Protect PII

```sql
-- Hash emails to preserve uniqueness without exposing PII
SELECT 
  MD5(email) as user_hash,
  purchase_amount
FROM transactions
```

---

### 8. Splitting

**Purpose**: Break columns into parts

```sql
-- Split email into prefix and domain
SELECT 
  SPLIT_PART(email, '@', 1) as email_prefix,
  SPLIT_PART(email, '@', 2) as email_domain
FROM users
```

---

### 9. Deduplication

**Purpose**: Remove redundant records

```sql
-- Keep only the earliest event per UUID
WITH ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY event_uuid 
      ORDER BY event_time ASC
    ) as rn
  FROM events
)
SELECT * FROM ranked WHERE rn = 1
```

---

## Update Patterns

### Overwrite

```sql
TRUNCATE TABLE target_table;
INSERT INTO target_table SELECT * FROM source;
```

### Insert (Append-only)

```sql
INSERT INTO transactions
SELECT * FROM staging_transactions
WHERE transaction_date = CURRENT_DATE;
```

### Upsert (MERGE)

```sql
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET
  t.name = s.name,
  t.updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN INSERT (id, name, created_at)
VALUES (s.id, s.name, CURRENT_TIMESTAMP);
```

### Soft Delete

```sql
UPDATE users
SET status = 'deleted', deleted_at = CURRENT_TIMESTAMP
WHERE user_id = 123;
```

### Hard Delete

```sql
DELETE FROM users WHERE user_id = 123;
```

---

## Best Practices

| Practice | Description |
| ---------- | ------------- |
| **Staging** | Always save intermediate states for recovery |
| **Idempotency** | Same input → same output (reruns don't duplicate) |
| **Incrementality** | Process only new/changed data |
| **Normalization** | Remove duplicates, ensure uniqueness |
| **Denormalization** | Add redundancy for query performance |
