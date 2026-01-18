# Beginner Concepts

Essential concepts for understanding DAX and the No CALCULATE approach.

---

## Row Context vs Filter Context

DAX has two types of "context" that determine what data a calculation can see:

### Filter Context

Created by:
- Slicers
- Visual axes (rows/columns)
- Report/page filters
- FILTER function in DAX

```dax
// This measure "sees" only rows matching the current filter context
Total Sales = SUMX( 'Sales', [Amount] )
```

### Row Context

Created during iteration (SUMX, FILTER, ADDCOLUMNS, etc.):

```dax
// Row context exists inside SUMX - we can reference [Amount] directly
Total = SUMX( 'Sales', [Amount] )

// Row context in FILTER - [Category] refers to the current row
Filtered = FILTER( 'Sales', [Category] = "Electronics" )
```

> [!NOTE]
> The No CALCULATE approach makes context **explicit** through variables and table functions. You can always see what data you're working with.

---

## Measures vs Calculated Columns

| Aspect | Measure | Calculated Column |
|--------|---------|-------------------|
| Calculated | At query time | At refresh time |
| Memory | None (computed live) | Stored in model |
| Row Context | No (aggregates) | Yes (per-row) |
| Use For | KPIs, aggregations | Sorting, filtering, relationships |

### When to Use Measures

- Aggregations (SUM, AVERAGE, COUNT)
- Ratios and percentages
- Anything that changes based on filters

### When to Use Calculated Columns

- You need to sort by the value
- You need to filter/slicer by the value
- You need a relationship key
- The calculation is static and row-based

> [!TIP]
> If you can do it in Power Query (M), do it there. It's more efficient than calculated columns.

---

## Variable Pattern

For the detailed variable pattern and standard measure templates, see [Core Pattern](./core-pattern.md). For the core tenets and philosophy, see [Philosophy](./philosophy.md).

---

## What Happens in a Visual

When you add fields to a visual, Power BI:

1. Creates **filter context** from row/column groupings
2. Evaluates each measure **per cell**
3. Combines with slicer/filter selections

```
Matrix Visual:
┌──────────┬─────────┬─────────┐
│ Category │ 2023    │ 2024    │
├──────────┼─────────┼─────────┤
│ Widgets  │ [Sales] │ [Sales] │  ← Each cell has its own filter context
│ Gadgets  │ [Sales] │ [Sales] │     (Category + Year)
└──────────┴─────────┴─────────┘
```

Your measure runs **once per cell**, with the cell's filters applied.

---

## Implicit vs Explicit Logic

> See [Philosophy: The No CALCULATE Alternative](./philosophy.md#the-no-calculate-alternative) for a side-by-side comparison of implicit `CALCULATE` code vs explicit "No CALCULATE" code.

---

## Common Beginner Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Using `/` for division | Divide-by-zero error | Use `DIVIDE(a, b, 0)` |
| Mixing column types | Type mismatch error | Ensure consistent data types |
| Missing relationship | Blank results | Check Model view for relationships |
| Circular reference | Error message | Break the dependency loop |
| Filtering on wrong table | Unexpected results | Filter the fact table, not dimension |
| Aggregation in calculated column | Same value for all rows | Aggregators break row context; use measures instead |
| Referencing column without table | Ambiguous reference error | Use `'Table'[Column]` not just `[Column]` in measures |
| Using TOTALYTD without calendar | Incorrect results | Use offsets approach or mark date table |
| Expecting row context in measures | BLANK or wrong aggregation | Measures have filter context only; use SUMX/iterator |
| SUM in calculated column | Returns grand total for every row | Use `[Column]` directly in calculated columns |


---

## Quick Debugging Checklist

For a distinct step-by-step debugging workflow and checklist, see [Debugging Techniques](./debugging.md).

---

## Model Best Practices

1. **Use a Calendar table** — Never use date columns from fact tables for time intelligence
2. **Star schema** — Facts in the center, dimensions radiating out
3. **Hide foreign keys** — Users shouldn't see `ProductID` on fact tables
4. **Sort by column** — Set Month to sort by MonthNum
5. **Mark date table** — Right-click > Mark as date table
