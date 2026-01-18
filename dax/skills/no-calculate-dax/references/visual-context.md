# Visual Context Patterns

Understanding how Power BI visuals create filter context and how to work with it.

---

## How Context Works

When a measure runs inside a visual, it receives **filter context** from:

1. **Internal filters** - Row/column headers in the visual itself
2. **External filters** - Slicers, other visuals, filter pane
3. **Page/Report filters** - Applied to entire page or report
4. **DAX filters** - Created by FILTER, ALL, etc. in your measure

---

## Auto-Exist Behavior

**Problem**: When two filters from the same table are active, Power BI only calculates for their **intersection**, not the full cross-product.

### Example Scenario
- Slicer on `'Sales'[Category]` = "Electronics"
- Visual axis on `'Sales'[Region]`

**Result**: Only regions with Electronics sales appear, not all regions.

### Why It Matters

Running totals or ALL calculations may return fewer rows than expected:

```dax
-- May return fewer dates than expected due to auto-exist
Running Total = 
    VAR __MaxDate = MAX( 'Sales'[Date] )
    VAR __Table = FILTER( ALL( 'Sales' ), [Date] <= __MaxDate )
    RETURN SUMX( __Table, [Amount] )
```

### Solution: Use Separate Tables

Move the axis column to a separate dimension table:

```dax
-- Fixed: Using separate Calendar table
Running Total = 
    VAR __MaxDate = MAX( 'Calendar'[Date] )
    VAR __Table = FILTER( ALL( 'Calendar' ), [Date] <= __MaxDate )
    RETURN SUMX( __Table, [Sales Amount] )
```

### Model Setting

Power BI has a model-level setting to control this:

**Location**: Model view > Properties > Value Filter Behavior

| Setting | Behavior |
|---------|----------|
| `Auto` (default) | Auto-exist applies |
| `Independent` | No auto-exist, full cross-product |

> **Warning**: Changing to `Independent` affects entire model and may impact performance.

---

## Context Detection Functions

For a complete reference of context detection functions (ISFILTERED, HASONEVALUE, ISINSCOPE, etc.), see [Function Reference: Context Detection](./function-reference.md#quick-reference).

---

## ALL, ALLSELECTED, ALLEXCEPT

For a detailed comparison of ALL, ALLSELECTED, and ALLEXCEPT, see [Function Reference: ALL vs ALLSELECTED](./function-reference.md#all-vs-allselected).

---

## Common Patterns

### Running Total (Context-Aware)

```dax
Running Total = 
    VAR __MaxDate = MAX( 'Calendar'[Date] )
    VAR __Table = FILTER( 
        ALLSELECTED( 'Calendar' ), 
        [Date] <= __MaxDate 
    )
    RETURN SUMX( __Table, [Sales] )
```

### Percentage of Parent

```dax
% of Parent = 
    VAR __Current = [Sales]
    VAR __Parent = IF(
        ISINSCOPE( 'Products'[SubCategory] ),
        SUMX( ALLEXCEPT( 'Sales', 'Products'[Category] ), [Amount] ),
        SUMX( ALL( 'Sales' ), [Amount] )
    )
    RETURN DIVIDE( __Current, __Parent )
```

### Rank Within Group

```dax
Rank in Category = 
    VAR __Current = [Sales]
    VAR __Category = MAX( 'Products'[Category] )
    VAR __Table = FILTER( 
        ALL( 'Products' ), 
        [Category] = __Category 
    )
    RETURN COUNTROWS( FILTER( __Table, [Sales] > __Current ) ) + 1
```

---

## Visual Consistency: The "Card vs Table" Trap

One of the strongest arguments for No CALCULATE is the inconsistent behavior of standard Time Intelligence functions (`TOTALYTD`, `SAMEPERIODLASTYEAR`) across different visual types.

> **Note**: This section shows a **context-aware variant** of the YTD pattern. For the core YTD pattern definition, see [Time Intelligence Patterns](./time-intelligence.md#period-to-date-generic-template).

### The Problem

Standard functions rely on implicit context detection, which often fails when the visual context changes:

**Scenario**: You have a `[Sales YTD]` measure using `TOTALYTD`.

1.  **In a Table Visual** (with Year column):
    - Works correctly for the *Current* year.
    - **Fail**: For *Past* years, it often returns the **Total Full Year** amount, not the "YTD up to today's date" amount. It cannot distinguish "same day last year" without complex CALCULATE logic.
    
2.  **In a Card Visual** (no date context):
    - **Fail**: Often returns `(Blank)` because it cannot determine the "current" date context without an explicit filter or date axis.

### The Solution: Offset Pattern

The No CALCULATE offset pattern handles both scenarios explicitly by checking context depth:

```dax
Year To Date = 
    -- 1. Check if we are in a specific year context (Table) or global context (Card)
    VAR __Offset = IF( 
        HASONEVALUE( 'Calendar'[Year] ), 
        MAX( 'Calendar'[CurrYearOffset] ), 
        0 -- Default to Current Year for Card visuals
    )
    
    -- 2. Define the max date boundary dynamically
    VAR __Today = TODAY()
    VAR __MaxDate = IF( __Offset = 0, __Today, MAX( 'Calendar'[Date] ) )
    
    -- 3. Filter explicitly using the determined variables
    VAR __Table = SUMMARIZE(
        FILTER( 'Calendar', [Date] <= __MaxDate && [CurrYearOffset] = __Offset ),
        [Date], "__Value", SUM( 'Sales'[Amount] )
    )
    RETURN SUMX( __Table, [__Value] )
```

**Why this is better**:
- **Table Visual**: `HASONEVALUE` is true, so it calculates correctly for every year row (even past years).
- **Card Visual**: `HASONEVALUE` is false, so it defaults to `0` (Current Year) and shows the correct current YTD total instead of Blank.
- **Consistency**: The logic is visible in the measure, not hidden in the engine.

---

## Visual Aggregation Defaults

When you add a numeric column to a visual, Power BI automatically aggregates it (usually SUM).

### Controlling Aggregation

In the Values well:
- Click dropdown → **Don't summarize** to show raw values
- This forces one row per data row instead of grouping

### When to Use Don't Summarize

- Showing individual transactions
- Displaying dates that should not be grouped
- Debugging to see actual row-level data

> **Note**: Setting a column to "Don't summarize" in a visual is different from changing the column's default aggregation in the model.

---

## Tooltip for Filter Debugging

Create a Card visual with this measure to see what filters are active:

```dax
Debug Context = 
    VAR __Filters = {
        IF( ISFILTERED( 'Calendar'[Year] ), "Year: " & MAX( 'Calendar'[Year] ), BLANK() ),
        IF( ISFILTERED( 'Calendar'[Month] ), "Month: " & MAX( 'Calendar'[Month] ), BLANK() ),
        IF( ISFILTERED( 'Products'[Category] ), "Category: " & MAX( 'Products'[Category] ), BLANK() )
    }
    RETURN CONCATENATEX( FILTER( __Filters, [Value] <> BLANK() ), [Value], UNICHAR(10) )
```

Add this Card to a tooltip page for on-demand debugging.

---

## Visual Interactions & Drill-Down

Patterns for handling specific visual behaviors like hierarchies, tooltips, and conditional formatting.

### Hierarchy & Drill-Down Logic

When using a Matrix or drill-down visual, use `ISINSCOPE` to detect which hierarchy level is currently active.

#### Context-Aware Hierarchy Measure

```dax
Hierarchy Sales = 
    SWITCH(
        TRUE(),
        -- Level 1: Product specific calculation
        ISINSCOPE( 'Product'[Current Product] ), [Sales Amount],
        
        -- Level 2: Category specific calculation
        ISINSCOPE( 'Product'[Category] ), [Sales Amount],
        
        -- Default / Grand Total
        [Sales Amount]
    )
```

### Custom Tooltips

Create visuals that appear on hover.

#### Tooltip Measure (Get Context)

To show "Top Product for [Selected Category]" in a tooltip:

```dax
Top Product in Tooltip = 
    VAR __Category = SELECTEDVALUE( 'Product'[Category] )
    VAR __Table = FILTER( ALL( 'Product' ), 'Product'[Category] = __Category )
    VAR __TopProduct = TOPN( 1, __Table, [Sales Amount] )
    VAR __Result = MAXX( __TopProduct, 'Product'[ProductName] )
    RETURN __Result
```

#### Percentage Difference Tooltip

Calculate difference from the bar you are hovering over compared to valid benchmark.

```dax
Tooltip vs Benchmark = 
    VAR __HoverValue = [Sales Amount]
    VAR __Benchmark = 100000 -- Or dynamic calculation
    VAR __Diff = __HoverValue - __Benchmark
    RETURN __Diff
```

### Visual Header Tooltips

Logic for the "?" icon in visual headers.

```dax
Header Help Text = 
    VAR __Context = "Sales for " & SELECTEDVALUE( 'Calendar'[Year], "All Years" )
    RETURN "This visual shows " & __Context & ". Drill down to see monthly details."
```

### Slicer Interaction Control

Using `EDIT RELATIONSHIP` equivalent logic (checking cross-filters)

```dax
Is Slicer Active = 
    IF( ISFILTERED( 'SlicerTable'[Column] ), "Filtered", "All" )
```

> **Usage**: Drop this measure into a visual card to debug whether a slicer is actually affecting the page context or if "Edit Interactions" has disabled it.

> **Note**: For all conditional formatting patterns including Gradients, Traffic Lights, and Transparent colors, see [Formatting Patterns](./formatting-patterns.md).

---

## Related References

- [Function Reference](./function-reference.md) — Quick reference for context detection functions (ISFILTERED, HASONEVALUE, ISINSCOPE, etc.)
- [Debugging Techniques](./debugging.md) — TOCSV, COUNTROWS inspection


