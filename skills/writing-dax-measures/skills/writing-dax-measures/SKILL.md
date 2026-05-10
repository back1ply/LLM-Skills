---
name: writing-dax-measures
description: This skill should be used when the user asks to "write DAX measures", "create Power BI calculations", "help with DAX formulas", "write time intelligence", or mentions aggregations, filters, or DAX performance. Ensures correct syntax, optimal performance, and best practices on the first attempt.
---

# Writing DAX Measures

## Overview

Generate correct DAX measures for Power BI on the first attempt by following pre-generation validation, avoiding anti-patterns, and applying proven best practices.

**Core principle**: Prompt quality exceeds model size. Accurate schema + avoiding anti-patterns + following best practices = first-try success.

## Scope

Applicable to DAX measure creation, Power BI calculations, DAX formulas, and aggregations/filters/time intelligence in Power BI context.

Not applicable to SQL queries, Excel formulas, Python/R data analysis, or other BI tools (Tableau, Qlik).

## Mandatory Pre-Generation Workflow

**BEFORE writing any DAX code, complete these steps in order:**

1. **Extract live schema** from Power BI MCP (use compact format for token efficiency)
2. **Verify all tables/columns** exist in schema (exact case-sensitive matching)
3. **Understand requirement type**:
   - Simple aggregation (SUM, COUNT, AVERAGE)
   - Calculation with logic (IF, SWITCH, COALESCE)
   - Time intelligence (YTD, MTD, PY, YoY)
   - Iterator pattern (SUMX, FILTER, RANKX)
4. **Identify filter context** requirements
5. **Choose output type**: Measure (default) vs. Calculated Column

## Forbidden Functions & Patterns

### Deprecated Functions (2026)

Never use these functions in new DAX code:

| Function | Why Forbidden | Use Instead |
| ---------- | --------------- | ------------- |
| `EARLIER()` | Deprecated, hard to maintain | `VAR` to save row context values |
| `IFERROR()` | Unreliable (misses errors), kills performance | `DIVIDE()` for division; design away errors |
| `ISERROR()` | Same issues as IFERROR | `DIVIDE()` for division; design away errors |
| `FIRSTNONBLANK()` | Poor performance (iterator) | `MIN()` or `MAX()` on column |
| `LASTNONBLANK()` | Poor performance (iterator) | `MIN()` or `MAX()` on column |

### Excel/SQL Functions That Don't Exist in DAX

| Don't Use | DAX Alternative |
| ----------- | ----------------- |
| `SUMIF`, `COUNTIF`, `AVERAGEIF` | `CALCULATE([Measure], filter)` |
| `VLOOKUP`, `HLOOKUP` | `RELATED()` or `LOOKUPVALUE()` |
| `SAMEPERIODLASTDAY` | Not a DAX function (typo of SAMEPERIODLASTYEAR) |

### Critical Anti-Patterns

**Never do these:**

```dax
❌ Naked CALCULATE without filters
CALCULATE([Sales])  -- Does nothing useful

❌ Division operator / (no error handling)
[Sales] / [Quantity]  -- Fails on zero

❌ FILTER on fact tables with scalar comparisons
FILTER(Sales, Sales[Amount] > 100)  -- Slow on large tables

❌ Filtering entire tables instead of columns
CALCULATE([Sales], FILTER(Products, ...))  -- Very slow

❌ Measures that never return BLANK
IF(ISBLANK([Sales]), 0, [Sales])  -- Hurts compression

❌ IF conditions inside iterators
SUMX(Sales, IF(Sales[Category] = "A", Sales[Amount], 0))  -- Use CALCULATE
```

## Performance Optimization Rules

### Filter Optimization (Critical for Performance)

#### Golden Rule: Filter columns, NOT tables

```dax
❌ BAD - Filters entire table
CALCULATE([Sales], FILTER(ALL(Products), Products[Category] = "Electronics"))

✅ GOOD - Filters column directly
CALCULATE([Sales], Products[Category] = "Electronics")
```

#### Filter Early Principle

```dax
❌ BAD - Complex logic first, then filter
VAR Result = [ComplexCalculation]
RETURN CALCULATE(Result, 'Date'[Year] = 2024)

✅ GOOD - Filter first, then calculate
CALCULATE([ComplexCalculation], 'Date'[Year] = 2024)
```

**Additional Filter Rules**:

- Filter lookup (dimension) tables, NOT fact tables
- Use Boolean expressions instead of FILTER when possible
- Use `CALCULATETABLE` instead of `FILTER` for table operations
- Use `REMOVEFILTERS` instead of `ALL` for clarity

### Variables for Performance & Clarity

Variables improve performance AND readability:

```dax
✅ Use VAR to:
- Avoid repetitive calculations (computed only once)
- Improve code readability
- Replace EARLIER pattern (deprecated)
- Store intermediate results
- Optimize IF conditions
- Cache measure values outside iterators
```

**Example**:

```dax
Total Sales Ratio =
VAR TotalSales = SUM(Sales[Amount])
VAR AllSales = CALCULATE(TotalSales, ALL(Sales))
RETURN
    DIVIDE(TotalSales, AllSales)
```

### Iterator Optimization

**Iterators are expensive - minimize usage**:

- Replace iterators with standard aggregations when possible: `SUM` >> `SUMX`
- Minimize nested iterators (expensive context transitions)
- Pre-aggregate with `SUMMARIZE` or `GROUPBY` to reduce rows
- Avoid IF inside iterators; use `CALCULATE` with filter instead
- Cache measure values with VAR outside iterator scope

```dax
❌ BAD - Iterator with IF condition
SUMX(Sales, IF(Sales[Amount] > 100, Sales[Amount], 0))

✅ GOOD - Filter first, then iterate
SUMX(FILTER(Sales, Sales[Amount] > 100), Sales[Amount])

✅ BETTER - Use CALCULATE if possible
CALCULATE(SUM(Sales[Amount]), Sales[Amount] > 100)
```

## Context Transition Rules

### Critical Understanding

1. **Measures are automatically wrapped in CALCULATE**
   - When you call a measure, it's automatically surrounded by CALCULATE
   - This triggers context transition: row context → filter context

2. **Context transition is expensive**
   - In each iteration, the model is re-filtered
   - For 1M rows with 10 columns = 1M filter operations

3. **Filter arguments of CALCULATE don't receive context transition**
   - Row context outside CALCULATE is available to filter arguments

### Best Practices

```dax
✅ Use SELECTEDVALUE() instead of VALUES()
-- VALUES() errors on multiple values
-- SELECTEDVALUE() returns BLANK on multiple values

✅ Be explicit about context
CALCULATE([Measure], FILTER(...))  -- Clear intent

✅ Cache measure values outside iterators
VAR MeasureValue = [Measure]
RETURN SUMX(Table, MeasureValue * Table[Column])
```

## Time Intelligence Patterns

### Date Table Requirements (CRITICAL)

The date table MUST satisfy these requirements:

✅ **Continuous dates**: All dates from Jan 1 to Dec 31 for all years
✅ **Marked as Date Table**: Apply "Mark as Date Table" setting in Power BI
✅ **One-to-many relationship**: Date table → Fact table
✅ **No gaps**: Every single day present in range

### Common Time Intelligence Patterns

```dax
# Year-to-Date
Sales YTD =
CALCULATE(
    [Total Sales],
    DATESYTD('Date'[Date])
)

# Previous Year
Sales PY =
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)

# Year-over-Year Growth %
YoY Growth % =
VAR CurrentYear = [Total Sales]
VAR PreviousYear = [Sales PY]
RETURN
    DIVIDE(CurrentYear - PreviousYear, PreviousYear)

# Month-to-Date
Sales MTD =
CALCULATE(
    [Total Sales],
    DATESMTD('Date'[Date])
)

# Quarter-to-Date
Sales QTD =
CALCULATE(
    [Total Sales],
    DATESQTD('Date'[Date])
)
```

**CRITICAL RULE**: Use time intelligence functions **only in filter arguments** of CALCULATE, never directly in iterators (triggers expensive context transitions).

## ALL vs ALLSELECTED vs ALLEXCEPT

Understanding these functions is critical for correct filter behavior:

| Function | Behavior | Use When |
| ---------- | ---------- | ---------- |
| `ALL(Table)` | Ignores ALL filters from everywhere | Global calculations, grand totals |
| `ALLSELECTED(Table)` | Ignores filters from within visual, keeps external filters | Dynamic totals respecting slicers |
| `ALLEXCEPT(Table, Col1, Col2)` | Removes all filters EXCEPT specified columns | Preserve specific dimensions |
| `REMOVEFILTERS(Table[Column])` | Clear syntax for removing filters | Preferred over ALL (better readability) |

**Default choice**: Use `ALLSELECTED` for user-friendly dashboards with slicers.

**Examples**:

```dax
# Grand Total (ignores ALL filters)
Grand Total Sales =
CALCULATE([Total Sales], ALL(Sales))

# Total Respecting Slicers (ignores only visual filters)
Dynamic Total =
CALCULATE([Total Sales], ALLSELECTED(Sales))

# Total by Region (keeps Region filter, removes others)
Total by Region =
CALCULATE([Total Sales], ALLEXCEPT(Sales, Sales[Region]))

# Clear specific filter (recommended syntax)
Sales Without Date Filter =
CALCULATE([Total Sales], REMOVEFILTERS('Date'))
```

## BLANK Handling

### How BLANK Works in DAX

- BLANK converts to **0** in sums and subtractions
- BLANK **propagates** in multiplication and division
- BLANK is NOT the same as SQL NULL
- Power BI automatically filters rows with BLANK values (performance optimization)

### BLANK Best Practices

```dax
✅ Let measures return BLANK naturally
-- Don't replace BLANK with 0 unless required
-- BLANK enables VertiPaq compression optimization

✅ Use DIVIDE() for safe division
DIVIDE([Numerator], [Denominator], 0)  -- Returns 0 on division by zero

✅ Use COALESCE() for first non-blank value
COALESCE([Measure1], [Measure2], [Measure3], 0)

✅ Use ISBLANK() to check before calculations
IF(ISBLANK([Measure]), 0, [Measure])  -- Only when UI requires no blanks

❌ Never create measures that never return BLANK
-- Kills VertiPaq compression and performance
```

## Measure vs Calculated Column

**Default: Always use Measures** unless you need physical column structure.

| Criterion | Measure | Calculated Column |
| ----------- | --------- | ------------------- |
| **Evaluation** | Query time (dynamic) | Refresh time (static) |
| **Storage** | No storage (code only) | Stored in model (uses RAM) |
| **Performance** | Better (on-demand calculation) | Slower refresh, consumes memory |
| **Filter Context** | Respects slicers/filters | Static per row |
| **Use Cases** | Aggregations, dynamic calculations | Slicers, row-level filters, static lookups |

**Use Calculated Columns only when**:

- Need to use result in slicer
- Need row-level filtering
- Performing static lookups with RELATED()

## Advanced Patterns

For relationships (USERELATIONSHIP, CROSSFILTER), running totals, rankings, moving averages, and percentage calculations, see [patterns.md](references/patterns.md).

## Naming Conventions & Documentation

### Naming Format

```dax
✅ Measures:      [Total Sales]
✅ Columns:       Products[Category]
✅ Tables:        Sales (be consistent: singular OR plural)
✅ Clear names:   [Year-over-Year Growth %]
❌ Abbreviations: [YoY_Grth_Pct]
```

### Documentation

```dax
✅ Add comments for complex logic
-- Calculate active customer sales only
-- Customers with purchases in last 90 days

✅ Use descriptive variable names
VAR ActiveCustomers = ...  -- Not just "AC"

✅ Format code for readability
-- Use DAX Formatter (daxformatter.com)
```

**Avoid**: Technical prefixes (dim_, fact_), cryptic abbreviations, unclear variable names

## Debugging

For debugging tools (DAX Studio, Tabular Editor), techniques, common errors and fixes, see [debugging.md](references/debugging.md).

## Pre-Submission Validation Checklist

**BEFORE submitting DAX code to user, verify:**

```text
□ All functions exist in DAX (no Excel/SQL functions)
□ All tables/columns match live schema exactly (case-sensitive)
□ No deprecated functions (EARLIER, IFERROR, ISERROR, FIRSTNONBLANK, LASTNONBLANK)
□ Context transitions are explicit and optimized
□ Variables used for repetitive calculations
□ DIVIDE() used instead of / operator
□ Filters applied to columns, not tables
□ Time intelligence functions only in filter arguments of CALCULATE
□ Measure naming follows convention: [Measure Name]
□ Comments added for complex logic
□ Code formatted for readability
```

## Quick Reference Table

| Task | DAX Pattern |
| ------ | ------------- |
| Safe division | `DIVIDE([Num], [Denom], 0)` |
| Remove filters | `REMOVEFILTERS(Table[Column])` |
| Remove all filters | `ALL(Table[Column])` |
| Keep slicer filters | `ALLSELECTED(Table)` |
| Store value | `VAR MyVal = [Measure]` then use `MyVal` |
| Single value from filter | `SELECTEDVALUE(Table[Column])` |
| Filter by value | `CALCULATE([Measure], Table[Column] = "Value")` |
| Year-to-date | `CALCULATE([Measure], DATESYTD('Date'[Date]))` |
| Previous year | `CALCULATE([Measure], SAMEPERIODLASTYEAR('Date'[Date]))` |
| Running total | `CALCULATE([Measure], FILTER(ALL('Date'), 'Date'[Date] <= MAX('Date'[Date])))` |
| Ranking | `RANKX(ALL(Table[Column]), [Measure], , DESC, DENSE)` |
| Check if blank | `IF(ISBLANK([Measure]), [Alternative], [Measure])` |
| First non-blank | `COALESCE([Measure1], [Measure2], 0)` |
| Related value | `RELATED(DimTable[Column])` |
| Lookup value | `LOOKUPVALUE(Table[Return], Table[Search], SearchValue)` |
