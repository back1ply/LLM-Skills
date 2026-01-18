# Source & Destination Evaluation Checklists

## Source Evaluation Checklist

Copy and fill for each data source:

```markdown
### Source: [Name]

| Question                       | Answer |
|--------------------------------|--------|
| Who will we collaborate with?  |        |
| How will the data be used?     |        |
| Are there multiple sources?    |        |
| What's the format?             |        |
| What's the frequency?          |        |
| What's the volume?             |        |
| What processing is required?   |        |
| How will the data be stored?   |        |
```

### Example: Payments Data

| Question                       | Answer                                   |
|--------------------------------|------------------------------------------|
| Who will we collaborate with?  | Engineering (Payments)                   |
| How will the data be used?     | Financial reporting, quarterly strategy  |
| Are there multiple sources?    | Yes (Stripe API + Internal DB)           |
| What's the format?             | Semi-structured JSON APIs                |
| What's the frequency?          | Hourly                                   |
| What's the volume?             | ~1K new rows/day, ~100K total            |
| What processing is required?   | Column renaming, enrichment              |
| How will the data be stored?   | Delta tables in Databricks               |

---

## Destination Evaluation Checklist

```markdown
### Destination: [Name]

| Question                          | Answer |
|-----------------------------------|--------|
| Who will we collaborate with?     |        |
| How will the data be used?        |        |
| Are there multiple destinations?  |        |
| What's the format?                |        |
| What's the frequency?             |        |
| What's the volume?                |        |
| What processing is required?      |        |
| How will the data be stored?      |        |
```

### Example: HR Analytics

| Question                          | Answer                                   |
|-----------------------------------|------------------------------------------|
| Who will we collaborate with?     | Human Resources                          |
| How will the data be used?        | Analyze tenure impact on results         |
| Are there multiple destinations?  | Yes (Delta Lake + Databricks SQL)        |
| What's the format?                | Parquet → structured tables              |
| What's the frequency?             | Batch (daily)                            |
| What's the volume?                | ~1K new rows/day, ~100K total            |
| What processing is required?      | LDP transformation, ML models            |
| How will the data be stored?      | Databricks SQL + external Delta tables   |

---

## Key Considerations

### For Sources

- **Upstream**: Work with software engineers on data contracts
- **Downstream**: Ensure analysts can use the data as intended
- Bias toward simplicity — question if each source is truly needed

### For Destinations

- **OLAP vs OLTP**: Analytics → OLAP (BigQuery, Redshift, Snowflake); Transactions → OLTP (Postgres)
- **Lakehouse**: Consider Delta Lake, Iceberg, or Hudi for combined benefits
- **Cost**: Warehouses have steeper storage costs than lakes
