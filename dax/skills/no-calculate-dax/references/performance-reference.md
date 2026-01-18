# Performance Reference

Best practices and benchmarks for writing efficient No CALCULATE DAX.

---

## Performance Optimization Patterns

Core principles for maintainable, performant DAX.

### Core Principles
1. **Filter early, filter often** — Reduce table sizes before aggregation.
2. **Cache repeated expressions** — Store in variables, evaluate once.
3. **Use appropriate functions** — Right tool for the job.

---

## Early Filtering

```dax
// ✓ Good: Filter first, then aggregate
Efficient = 
    VAR __Table = FILTER( 'Sales', 'Sales'[Year] = 2024 )
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result

// ✗ Bad: Aggregating over full table with condition
Inefficient = 
    SUMX( 'Sales', IF( 'Sales'[Year] = 2024, [Amount], 0 ) )
```

---

## Variable Caching

```dax
// ✓ Good: Calculate once, use many times
Efficient Ratio = 
    VAR __Revenue = SUMX( 'Sales', [Amount] )
    VAR __Cost = SUMX( 'Sales', [Cost] )
    VAR __Margin = __Revenue - __Cost
    VAR __Pct = DIVIDE( __Margin, __Revenue )
    VAR __Result = IF( __Pct > 0.2, "High", "Low" )
    RETURN __Result

// ✗ Bad: Recalculating __Revenue twice
Inefficient = 
    IF( 
        DIVIDE( SUMX('Sales',[Amount]) - SUMX('Sales',[Cost]), SUMX('Sales',[Amount]) ) > 0.2,
        "High",
        "Low" 
    )
```

---

## SUMMARIZE vs SUMMARIZECOLUMNS vs GROUPBY

See [Table Functions: SUMMARIZE vs SUMMARIZECOLUMNS](table-functions.md#summarize-vs-summarizecolumns-vs-groupby) for the detailed comparison and performance implications.

---

## SWITCH TRUE vs Nested IF

For readability and multi-condition branching, prefer `SWITCH(TRUE(), ...)` over nested `IF` statements.

> **See**: [Function Reference: SWITCH TRUE](./function-reference.md#switch-true-pattern) for full examples and explanation.

---

## Short-Circuiting Evaluation

DAX uses short-circuit evaluation. Put the most restrictive or fastest check *first* in your conditions.

```dax
// If Quantity is 0, the expensive RELATED check is skipped entirely
FILTER( 'Sales', 'Sales'[Quantity] > 0 && RELATED( 'Product'[ExpensiveCategory] ) = TRUE )
```

---

## Avoid Expensive Operations in Filters

```dax
// ✗ Avoid: Calling measures inside FILTER
Slow = 
    VAR __Table = FILTER( 'Products', [Expensive Measure] > 100 )
    RETURN COUNTROWS( __Table )

// ✓ Better: Pre‑calculate and filter on column
Fast = 
    VAR __Threshold = 100
    VAR __Table = FILTER( 
        ADDCOLUMNS( 'Products', "__CalcValue", [Simple Column Calc] ),
        [__CalcValue] > __Threshold 
    )
    RETURN COUNTROWS( __Table )
```

---

## DISTINCT vs VALUES

See [Function Reference: DISTINCT vs VALUES](function-reference.md#distinct-vs-values) for detailed comparison.

---

## Optimizing Interval Overlaps (Events in Progress)

```dax
Active Events = 
    VAR __MinDate = MIN( 'Dates'[Date] )
    VAR __MaxDate = MAX( 'Dates'[Date] )
    VAR __Table = FILTER( 
        'Events', 
        'Events'[StartDate] <= __MaxDate &&
        'Events'[EndDate] >= __MinDate 
    )
    RETURN COUNTROWS( __Table )
```

---

## Debugging Performance

Use DAX Studio or Performance Analyzer to identify slow measures:
1. **Performance Analyzer** (Power BI): View → Performance Analyzer → Start Recording
2. **DAX Studio**: Connect to model, run queries with timing

### Common Performance Issues
| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Slow visuals | Measure too complex | Break into variables |
| Memory spikes | Large intermediate tables | Filter earlier |
| Slow refresh | Calculated columns | Move to Power Query |
| Timeout | Cartesian explosion | Avoid unnecessary CROSSJOIN |

---

## When to Use Calculated Columns vs Measures

See [Beginner Concepts: Measures vs Columns](beginner-concepts.md#measures-vs-calculated-columns) for detailed comparison.

---

## Related References
- [Visual Context](visual-context.md) – Understanding Auto‑exist and filter context.

---

## Benchmarks Summary

| Scenario | Standard (CALCULATE) | No‑Calc |
|----------|----------------------|--------|
| Time Intelligence (TOTALYTD) | 357 ms | 318 ms |
| Conditional Sum (simple filter) | 125 ms | 140 ms |
| Complex Iteration (ranking) | 2550 ms | 2000 ms |

*Key Takeaway*: No‑Calc offers comparable or better performance in complex scenarios while providing clearer, debuggable logic.
