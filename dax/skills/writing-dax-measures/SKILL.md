---
name: writing-dax-measures
description: Use when writing DAX measures for Power BI, before generating any DAX code, to ensure correct syntax, optimal performance, and adherence to best practices on the first attempt
---

# Writing DAX Measures

## Overview

Generate correct DAX measures for Power BI on the first attempt by following pre-generation validation, avoiding anti-patterns, and applying proven best practices.

**Core principle**: Prompt quality exceeds model size. Accurate schema + avoiding anti-patterns + following best practices = first-try success.

## When to Use

Use this skill when:
- User requests DAX measure creation
- User asks to write Power BI calculations
- User needs help with DAX formulas
- User mentions aggregations, filters, or time intelligence in Power BI context

Do NOT use for:
- SQL queries
- Excel formulas
- Python/R data analysis
- Other BI tools (Tableau, Qlik)

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
|----------|---------------|-------------|
| `EARLIER()` | Deprecated, hard to maintain | `VAR` to save row context values |
| `IFERROR()` | Unreliable (misses errors), kills performance | `DIVIDE()` for division; design away errors |
| `ISERROR()` | Same issues as IFERROR | `DIVIDE()` for division; design away errors |
| `FIRSTNONBLANK()` | Poor performance (iterator) | `MIN()` or `MAX()` on column |
| `LASTNONBLANK()` | Poor performance (iterator) | `MIN()` or `MAX()` on column |

### Excel/SQL Functions That Don't Exist in DAX

| Don't Use | DAX Alternative |
|-----------|-----------------|
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

**Golden Rule: Filter columns, NOT tables**

```dax
❌ BAD - Filters entire table
CALCULATE([Sales], FILTER(ALL(Products), Products[Category] = "Electronics"))

✅ GOOD - Filters column directly
CALCULATE([Sales], Products[Category] = "Electronics")
```

**Filter Early Principle**

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

Your date table MUST satisfy these requirements:

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
|----------|----------|----------|
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

### Best Practices

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
|-----------|---------|-------------------|
| **Evaluation** | Query time (dynamic) | Refresh time (static) |
| **Storage** | No storage (code only) | Stored in model (uses RAM) |
| **Performance** | Better (on-demand calculation) | Slower refresh, consumes memory |
| **Filter Context** | Respects slicers/filters | Static per row |
| **Use Cases** | Aggregations, dynamic calculations | Slicers, row-level filters, static lookups |

**Use Calculated Columns only when**:
- Need to use result in slicer
- Need row-level filtering
- Performing static lookups with RELATED()

## Relationships & Cross-Filtering

### USERELATIONSHIP - Activate Inactive Relationships

```dax
Sales (Ship Date) =
CALCULATE(
    [Total Sales],
    USERELATIONSHIP(Sales[ShipDate], 'Date'[Date])
)
```

Use when you have multiple date columns (OrderDate, ShipDate, DueDate) and need to activate alternate relationship.

### CROSSFILTER - Override Relationship Direction

```dax
Sales Both Ways =
CALCULATE(
    [Total Sales],
    CROSSFILTER(Products[ProductKey], Sales[ProductKey], BOTH)
)
```

**Options**: `NONE`, `SINGLE` (one direction), `BOTH` (bidirectional)

**Best Practice**: Use physical relationships when possible; reserve DAX overrides for specific measure calculations.

## Common Calculation Patterns

### Running Totals / Cumulative

```dax
Cumulative Sales =
CALCULATE(
    [Total Sales],
    FILTER(
        ALL('Date'[Date]),
        'Date'[Date] <= MAX('Date'[Date])
    )
)
```

### Ranking

```dax
Product Rank =
RANKX(
    ALL(Products[ProductName]),
    [Total Sales],
    ,
    DESC,
    DENSE
)
```

**RANKX parameters**: Table, Expression, Value, Order (ASC/DESC), Ties (SKIP/DENSE)

### Moving Average

```dax
Moving Average 3 Months =
VAR CurrentDate = MAX('Date'[Date])
VAR DateRange =
    DATESINPERIOD(
        'Date'[Date],
        CurrentDate,
        -3,
        MONTH
    )
RETURN
    CALCULATE(
        AVERAGE(Sales[Amount]),
        DateRange
    )
```

### Percentage of Total

```dax
% of Grand Total =
VAR CurrentSales = [Total Sales]
VAR TotalSales = CALCULATE([Total Sales], ALL(Sales))
RETURN
    DIVIDE(CurrentSales, TotalSales)
```

### Same Period Last Year

```dax
Sales Same Period Last Year =
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR('Date'[Date])
)
```

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

## Debugging Techniques

### Tools

1. **DAX Studio** - Query plan analysis, performance analyzer
2. **Tabular Editor 3** - DAX debugger with breakpoints, watch windows
3. **Variables** - Return intermediate values for inspection

### Debug with Variables

```dax
Debug Measure =
VAR Step1 = SUM(Sales[Amount])
VAR Step2 = CALCULATE(Step1, ALL(Products))
VAR Step3 = DIVIDE(Step1, Step2)
-- RETURN Step1  -- Debug: Check Step1
-- RETURN Step2  -- Debug: Check Step2
RETURN Step3     -- Final result
```

### Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Circular dependency | Column references itself in chain | Break loop with different table/approach |
| Column doesn't exist | Typo or wrong table reference | Verify against live schema extraction |
| Division by zero | No safeguard | Use `DIVIDE()` instead of `/` |
| Context transition issue | Measure called in iterator | Cache with VAR outside iterator |
| Function doesn't exist | Excel/SQL function used | Check against DAX function reference |

## Pre-Submission Validation Checklist

**BEFORE submitting DAX code to user, verify:**

```
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
|------|-------------|
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

## Real-World Impact

Following these practices enables:
- **First-try success**: Correct DAX on initial generation
- **Optimal performance**: Queries execute faster with proper filtering
- **Maintainable code**: Clear naming and structure for future modifications
- **Avoided pitfalls**: No deprecated functions or anti-patterns
- **Professional quality**: Industry best practices from SQLBI, Microsoft, and DAX experts

## Common Mistakes to Avoid

1. **Using Excel formulas** in DAX (SUMIF, VLOOKUP)
2. **Filtering tables** instead of columns
3. **Not using variables** for repeated calculations
4. **Forgetting date table** requirements for time intelligence
5. **Using IFERROR** instead of designing away errors
6. **Creating measures that never return BLANK**
7. **Using deprecated EARLIER** instead of VAR
8. **Complex logic in iterators** instead of pre-filtering
9. **Not extracting live schema** before writing DAX
10. **Ignoring context transition** performance costs
