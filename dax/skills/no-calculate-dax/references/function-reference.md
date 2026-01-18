# Function Reference

Quick reference for key DAX functions in the No CALCULATE approach.

### ALL vs ALLSELECTED

See [Table Functions Reference: ALL Functions](./table-functions.md#all-functions) for a detailed comparison and patterns.

---

## % of Total Patterns

See [Table Functions Reference: % of Total Patterns](./table-functions.md#percent-of-total-patterns) for implementation details.

---

## HASONEVALUE Pattern

Detect if a single value is in context (e.g., distinguishing detail rows from totals):

```dax
Conditional Measure = 
    VAR __IsSingleYear = HASONEVALUE( 'Calendar'[Year] )
    VAR __Offset = IF( __IsSingleYear, MAX( 'Calendar'[CurrYearOffset] ), 0 )
    VAR __Table = FILTER( ALL( 'Calendar' ), [CurrYearOffset] = __Offset )
    VAR __Result = SUMX( __Table, [Sales Amount] )
    RETURN __Result
```

### Common HASONEVALUE Uses

| Pattern | Code |
|---------|------|
| Detect Total row | `IF( NOT HASONEVALUE( 'Table'[Category] ), "Total", MAX( 'Table'[Category] ) )` |
| Dynamic label | `IF( HASONEVALUE( 'Dates'[Month] ), MAX( 'Dates'[Month] ), "All Months" )` |
| Conditional logic | `IF( HASONEVALUE( ... ), detail calculation, total calculation )` |

---

## ISINSCOPE Pattern

Detect which level of a hierarchy is in scope (for Matrix visuals with row hierarchies):

```dax
Level Indicator = 
    VAR __Result = SWITCH(
        TRUE(),
        ISINSCOPE( 'Table'[Product] ), 3,      -- Deepest level first!
        ISINSCOPE( 'Table'[Category] ), 2,
        ISINSCOPE( 'Table'[Department] ), 1,
        0                                       -- Total row
    )
    RETURN __Result
```

> [!IMPORTANT]
> Test levels from deepest to shallowest. Higher levels are technically "in scope" at lower levels too.

### Conditional Total Formatting

```dax
Show Only At Total = 
    IF( 
        NOT ISINSCOPE( 'Table'[Category] ), 
        [Complex Calculation],  -- Only at Total row
        BLANK() 
    )
```

### Common ISINSCOPE Uses

| Pattern | Code |
|---------|------|
| Detect detail row | `IF( ISINSCOPE( 'Table'[Item] ), "Detail", "Subtotal" )` |
| Hierarchy-aware measure | `SWITCH( TRUE(), ISINSCOPE([Product]), [Product Calc], ISINSCOPE([Category]), [Category Calc], [Total Calc] )` |
| Conditional formatting | Return different colors based on level |

---

> **See Also**: [Time Intelligence Patterns](./time-intelligence.md#running-total) for Running Total and cumulative patterns.

## DISTINCT vs VALUES

See [Table Functions Reference: DISTINCT vs VALUES](./table-functions.md#distinct-vs-values) for a detailed comparison.

**Recommendation**: Use `DISTINCT` unless you specifically need to detect missing relationships.

---

## SUMMARIZE and Grouping

> **See**: [Table Functions Reference](./table-functions.md#summarize-vs-summarizecolumns-vs-groupby) for detailed comparison of grouping functions.

---

## EARLIER

> **Note**: `EARLIER` is rarely needed in modern DAX. Use Variables or `ADDCOLUMNS` iteration instead.

---

## Table Manipulation Functions
 
For table manipulation functions including `SELECTCOLUMNS`, `DATATABLE`, the `IN` operator, and `CONTAINSROW`, please refer to the comprehensive [Table Functions Reference](./table-functions.md).
 
 > **Includes**:
 > - `SELECTCOLUMNS` - Project specific columns
 > - `DATATABLE` - Create inline tables
 > - `IN` / `NOT IN` - Multiple value matching
 > - `CONTAINSROW` - Row existence check


---

## COALESCE (First Non-Blank)

Return the first non-blank value from a list:

```dax
First Available = 
    COALESCE( 
        [Preferred Value], 
        [Backup Value], 
        [Default Value],
        0  // Final fallback
    )
```

Common use - replace blanks with a default:

```dax
Value Or Zero = COALESCE( [Sales], 0 )

Value Or Text = COALESCE( [Name], "Unknown" )
```

---



---

## ISBLANK / BLANK Handling

Check for blanks in different scenarios:

```dax
// Check if value is blank
Is Empty = ISBLANK( [Value] )

// Safe value extraction (avoids blank propagation)
Safe Value = IF( ISBLANK( [Value] ), 0, [Value] )

// Generate explicit blank
Return Blank = BLANK()

// ISBLANK vs COALESCE comparison
Using ISBLANK = IF( ISBLANK( [Value] ), "N/A", [Value] )
Using COALESCE = COALESCE( [Value], "N/A" )  // Simpler
```

---

## SWITCH TRUE Pattern

Multi-condition branching (cleaner than nested IF).

> [!TIP]
> **Why TRUE() is preferred**: It handles ranges (e.g. `[Age] > 18`), evaluates strictly top-to-bottom, and is far more readable than nested `IF()` statements.

```dax
Category = 
    VAR __Value = [Score]
    RETURN SWITCH(
        TRUE(),
        __Value >= 90, "A",
        __Value >= 80, "B", 
        __Value >= 70, "C",
        __Value >= 60, "D",
        "F"
    )
```

> [!TIP]
> Conditions are evaluated top-to-bottom; first TRUE match wins.

---

## TREATAS (Virtual Relationship)

Apply filter from one table to another without a model relationship:

```dax
Sales via Disconnected Slicer = 
    VAR __Selections = VALUES( 'Slicer'[Product] )
    VAR __Filter = TREATAS( __Selections, 'Sales'[Product] )
    VAR __Table = FILTER( ALL( 'Sales' ), 'Sales'[Product] IN __Filter )
    RETURN SUMX( __Table, [Amount] )
```

> [!IMPORTANT]
> TREATAS is one of the few places where CALCULATE-like behavior may be useful. The No CALCULATE equivalent uses `IN` operator instead.

---

## When CALCULATE Is Acceptable

While this skill avoids CALCULATE, there are specific scenarios where it can be practical:

### 1. Wrapping an Existing Measure

When you need to call an existing measure in a slightly modified context without duplicating all its logic:

```dax
// Reusing an existing measure with a simple override
Sales Red Only = 
    VAR __Base = [Total Sales]  // Existing complex measure
    // If you truly need to override context, CALCULATE can wrap it
    // But prefer the No CALCULATE approach when writing new measures
    RETURN __Base
```

### 2. Simple ALL Override (No Debugging Needed)

```dax
// Acceptable when the logic is trivial and obvious
% of All = DIVIDE( [Sales], CALCULATE( [Sales], ALL( 'Products' ) ) )
```

### 3. Time Intelligence Shortcuts (Legacy Code)

When maintaining existing code that uses TOTALYTD, SAMEPERIODLASTYEAR, etc., it may be practical to keep them rather than refactor.

### When NOT to Use CALCULATE

For the full explanation of why to avoid CALCULATE and the core tenets, see **[Philosophy](./philosophy.md)**.

**Quick summary**: Prefer explicit `FILTER` + `VAR` for complex filtering, debugging, and new measure development.

> Use CALCULATE only when you **fully understand** its filter‑modification behavior and can **debug any issues** that arise. For complex logic, **always prefer the explicit variable pattern**.

---

## Quick Reference

| Function | Purpose |
|----------|---------|
| `ISFILTERED(col)` | Is column directly filtered? |
| `ISCROSSFILTERED(table)` | Is table filtered (directly or via relationship)? |
| `HASONEVALUE(col)` | Exactly one value in context? |
| `ISINSCOPE(col)` | Is column grouping in matrix? |
| `SELECTEDVALUE(col, alt)` | Get single value or alternate |
| `FILTERS(col)` | Table of active filter values |
| `ALL(table)` | Remove all filters |
| `ALLSELECTED(table)` | Keep external filters only |
| `ALLEXCEPT(table, cols)` | Keep only specified columns filtered |
| `COALESCE(val1, val2, ...)` | First non-blank value |
| `DATATABLE(...)` | Create inline typed table |
| `TREATAS(table, col)` | Virtual relationship |

