# Orchestration Patterns Reference

## Core Concepts

### DAG (Directed Acyclic Graph)

- **Directed**: Tasks execute in a specific order
- **Acyclic**: No circular dependencies (no loops)
- **Tasks**: Individual units of work (nodes)
- **Dependencies**: Relationships between tasks (edges)

```text
Extract → Transform → Load → Validate
    ↘                    ↗
      Enrich ──────────→
```

---

## Orchestration Patterns

### 1. Backfills

**Problem**: Need historical data before pipeline existed

**Pattern**: Build pipelines that can recreate past data

```python
# Airflow example - set start_date in the past
dag = DAG(
    'daily_etl',
    start_date=datetime(2024, 1, 1),  # Will backfill from this date
    schedule_interval='@daily',
    catchup=True  # Enable backfilling
)
```

**Requirements**:

- Idempotent pipelines (reruns produce same results)
- Parameterized date handling
- Source data still accessible

---

### 2. Event-Driven Orchestration

**Problem**: Cron schedules don't align with data availability

**Pattern**: Trigger on events, not schedules

```yaml
# Trigger when upstream completes
trigger:
  type: pipeline_completion
  pipeline: fivetran_sync
  
# Or trigger on file arrival
trigger:
  type: file_arrival
  path: s3://bucket/data/*.parquet
```

**Benefits**:

- Data as fresh as possible
- No wasted runs on empty data
- Avoids race conditions

---

### 3. Conditional Logic

**Problem**: Different scenarios need different handling

**Pattern**: Branch based on conditions

```python
# Airflow BranchPythonOperator
def choose_path(**context):
    if context['params']['data_volume'] > 1000000:
        return 'heavy_processing'
    else:
        return 'light_processing'

branch = BranchPythonOperator(
    task_id='choose_processing',
    python_callable=choose_path
)
```

---

### 4. Concurrency (Dynamic Tasks)

**Problem**: Many small files/tasks bottleneck processing

**Pattern**: Fan out parallel tasks

```python
# Airflow dynamic task mapping
@task
def process_file(file_path: str):
    # Process single file
    pass

@task
def get_files():
    return ['file1.csv', 'file2.csv', 'file3.csv']

# Expand dynamically
files = get_files()
process_file.expand(file_path=files)
```

---

### 5. Retry and Fallback

**Problem**: Transient failures break pipelines

**Pattern**: Automatic retries with fallback logic

```python
# Airflow task with retries
task = PythonOperator(
    task_id='fetch_api',
    python_callable=fetch_data,
    retries=3,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True
)
```

**Fallback pattern**:

```text
Try API → Success → Continue
    ↓
  Fail → Retry (3x)
    ↓
  Fail → Fallback (cached data or alert)
```

---

### 6. Parameterized Execution

**Problem**: Need flexibility for different runs

**Pattern**: Accept parameters at runtime

```python
# Airflow DAG with parameters
dag = DAG('parameterized_etl', params={
    'start_date': Param(default='{{ ds }}'),
    'region': Param(default='US', enum=['US', 'EU', 'APAC'])
})

# Use in tasks
sql = """
SELECT * FROM sales 
WHERE date = '{{ params.start_date }}'
AND region = '{{ params.region }}'
"""
```

---

### 7. Pipeline Decomposition

**Problem**: Monolithic DAGs are fragile

**Pattern**: Break into micro-DAGs

```text
Meta-DAG (orchestrates other DAGs):
  ├── Ingestion DAG
  ├── Bronze→Silver DAG
  ├── Silver→Gold DAG
  └── Validation DAG
```

**Benefits**:

- Isolated failures
- Easier debugging
- Independent development
- Selective reruns

---

### 8. Lineage Tracking

**Problem**: Can't trace data origin or debug issues

**Pattern**: Track data flow at column level

```sql
-- dbt example with documentation
{{ config(materialized='table') }}

SELECT
  order_id,      -- from: raw.orders.id
  user_name,     -- from: users.full_name (enriched)
  total_amount   -- calculated: SUM(line_items.amount)
FROM {{ ref('stg_orders') }}
JOIN {{ ref('dim_users') }} USING (user_id)
```

---

## Orchestrator Comparison

| Feature            | Airflow | Dagster | Prefect | dbt | Lakeflow |
|--------------------|---------|---------|---------|-----|----------|
| Task orchestration | ✅      | ✅      | ✅      | ❌  | ✅       |
| SQL orchestration  | ❌      | ❌      | ❌      | ✅  | ✅       |
| Asset-based        | ❌      | ✅      | ✅      | ✅  | ✅       |
| Managed option     | ✅      | ✅      | ✅      | ✅  | ✅       |
| Open source        | ✅      | ✅      | ✅      | ✅  | ❌       |

---

## Anti-Patterns

| Anti-Pattern                 | Problem                                    | Solution                           |
|------------------------------|--------------------------------------------|------------------------------------|
| Orchestrator as transformer  | Overloads orchestrator, poor visibility    | Trigger external services          |
| Monolithic DAGs              | One failure breaks everything              | Decompose into micro-DAGs          |
| Missing backfill logic       | Can't recover historical data              | Build backfill into design         |
| Schedule-only triggers       | Wasted runs, stale data                    | Add event-driven triggers          |
| No retry logic               | Transient failures cause outages           | Configure retries with backoff     |
