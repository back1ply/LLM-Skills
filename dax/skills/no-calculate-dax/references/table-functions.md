# Table Functions Reference

Core table manipulation functions for the No CALCULATE approach. Understanding these functions is fundamental to writing effective DAX.

---

## Table Creation Functions

### FILTER - Core Filtering Function

Filter rows based on conditions:

```dax
Sales Red =
    VAR __Table = FILTER( 'Sales', 'Sales'[Color] = "Red" )
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result
```

**Multiple conditions:**

```dax
Filtered Sales =
    VAR __Table = FILTER(
        'Sales',
        'Sales'[Color] = "Red" && 'Sales'[Amount] > 100
    )
    RETURN SUMX( __Table, [Amount] )
```

> [!TIP]
> Filter early in your variable chain to reduce table size for downstream operations.

---

### SUMMARIZE vs SUMMARIZECOLUMNS vs GROUPBY

All three group rows, but have different behaviors:

#### SUMMARIZE (Most Common)

Groups rows and optionally adds aggregations:

```dax
Sales by Category =
    VAR __Table = SUMMARIZE(
        'Sales',
        'Sales'[Category],
        "__Total", SUM( 'Sales'[Amount] ),
        "__Count", COUNTROWS( 'Sales' )
    )
    RETURN __Table
```

**Use when:**
- You need to group by columns from multiple tables
- You want to add aggregations while grouping
- You need to work with filter context

#### GROUPBY (Better Performance)

Similar to SUMMARIZE but doesn't automatically create filter context:

```dax
Sales by Category =
    VAR __Table = GROUPBY(
        'Sales',
        'Sales'[Category],
        "__Total", SUMX( CURRENTGROUP(), 'Sales'[Amount] ),
        "__Count", COUNTROWS( CURRENTGROUP() )
    )
    RETURN __Table
```

**Use when:**
- Performance is critical
- You're grouping within a single table
- You want more control over aggregation context

**Key Difference:** GROUPBY requires CURRENTGROUP() for aggregations, SUMMARIZE doesn't.

#### SUMMARIZECOLUMNS (Advanced)

Most performant but complex:

```dax
Sales Summary =
    SUMMARIZECOLUMNS(
        'Product'[Category],
        'Calendar'[Year],
        "Total", SUM( 'Sales'[Amount] )
    )
```

**Use when:**
- Building DAX queries (not measures)
- Performance is absolutely critical
- You understand its filter context behavior

**Avoid in measures:** Unpredictable filter context interactions.

---

### ADDCOLUMNS - Add Calculated Columns

Add new columns to an existing table:

```dax
Enhanced Sales =
    VAR __Table = ADDCOLUMNS(
        'Sales',
        "__Margin", [Price] - [Cost],
        "__MarginPct", DIVIDE( [Price] - [Cost], [Price], 0 )
    )
    RETURN __Table
```

**Chaining ADDCOLUMNS:**

```dax
Multi-Step Calculation =
    VAR __Step1 = ADDCOLUMNS(
        'Sales',
        "__Revenue", [Quantity] * [Price]
    )
    VAR __Step2 = ADDCOLUMNS(
        __Step1,
        "__Cost", [Quantity] * [UnitCost],
        "__Profit", [__Revenue] - [__Cost]
    )
    RETURN SUMX( __Step2, [__Profit] )
```

> [!IMPORTANT]
> Multiple ADDCOLUMNS calls are less efficient than one call with multiple columns.

---

### SELECTCOLUMNS - Project Specific Columns

Select and optionally rename columns:

```dax
Customer IDs =
    VAR __Table = SELECTCOLUMNS(
        'Sales',
        "ID", 'Sales'[CustomerID],
        "Date", 'Sales'[OrderDate]
    )
    RETURN __Table
```

**When to use:**
- Reducing table width for performance
- Renaming columns for clarity
- Preparing tables for UNION/EXCEPT/INTERSECT

**vs ADDCOLUMNS:**
- SELECTCOLUMNS: Choose which columns to keep
- ADDCOLUMNS: Keep all columns + add new ones

---

### DISTINCT vs VALUES

| Function | Returns | Includes BLANK? |
|----------|---------|-----------------|
| `DISTINCT( 'Table'[Column] )` | Unique values only | No |
| `VALUES( 'Table'[Column] )` | Unique values + blank if relationship missing | Yes |

**Rule of thumb:** Use DISTINCT for column value lists, VALUES when you need BLANK handling.

---

### ALL Functions

| Function | Removes | Use Case |
|----------|---------|----------|
| `ALL('Table')` | ALL filters (internal + external) | Grand totals, % of total |
| `ALLSELECTED('Table')` | Only internal visual filters | Subtotals respecting slicers |

---

### % of Total Patterns

#### % of Grand Total (ALL)

```dax
% of Total = 
    VAR __Current = SUM( 'Sales'[Amount] )
    VAR __Total = SUMX( ALL( 'Sales' ), [Amount] )
    RETURN DIVIDE( __Current, __Total, 0 )
```

#### % of Selected Total (ALLSELECTED)

```dax
% of Selected = 
    VAR __Current = SUM( 'Sales'[Amount] )
    VAR __Total = SUMX( ALLSELECTED( 'Sales' ), [Amount] )
    RETURN DIVIDE( __Current, __Total, 0 )
```

---

## Table Manipulation Functions

### ROW - Create Single-Row Table

```dax
Single Row =
    VAR __Table = ROW(
        "Category", "Electronics",
        "Amount", 1000,
        "Date", DATE( 2024, 1, 1 )
    )
    RETURN __Table
```

**Use for:**
- Creating test data
- Default values
- Parameter tables (combine with UNION)

---

### DATATABLE - Create Inline Lookup Table

```dax
Color Lookup =
    DATATABLE(
        "Color", STRING,
        "Priority", INTEGER,
        {
            { "Red", 1 },
            { "Yellow", 2 },
            { "Green", 3 }
        }
    )
```

**Use for:**
- Small lookup tables
- Parameter tables
- Testing without creating model tables

---

### GENERATESERIES - Generate Numeric Sequence

```dax
Numbers 1 to 100 = GENERATESERIES( 1, 100, 1 )

-- With step size
Even Numbers = GENERATESERIES( 0, 100, 2 )

-- For loops/iteration
Running Calculation =
    VAR __MaxRow = 100
    VAR __Table = ADDCOLUMNS(
        GENERATESERIES( 1, __MaxRow ),
        "__Value", [Value] * 2
    )
    RETURN __Table
```

---

### GENERATE - Cross Join Tables

Create all combinations of two tables:

```dax
All Combinations =
    VAR __Table = GENERATE(
        DISTINCT( 'Sales'[Category] ),
        DISTINCT( 'Calendar'[Year] )
    )
    RETURN __Table
```

**Practical Example - Expanding Date Ranges:**

```dax
-- Create one row per day for each project
Project Days =
    GENERATE(
        'Projects',
        FILTER(
            'Calendar',
            'Calendar'[Date] >= [StartDate] &&
            'Calendar'[Date] <= [EndDate]
        )
    )
```

---

## Set Operations

### UNION - Combine Tables Vertically

Append rows from multiple tables:

```dax
Combined = UNION( 'Table1', 'Table2', 'Table3' )
```

**Must have:**
- Same number of columns
- Matching column data types (in order)

**Practical Example:**

```dax
Period Selector =
    UNION(
        ROW( "Label", "Last 7 Days", "Days", 7 ),
        ROW( "Label", "Last 30 Days", "Days", 30 ),
        ROW( "Label", "Last 90 Days", "Days", 90 ),
        ROW( "Label", "Year to Date", "Days", -1 )
    )
```

---

### EXCEPT - Rows in First NOT in Second

```dax
New Customers =
    VAR __Current = DISTINCT( 'Sales'[CustomerID] )
    VAR __Previous = DISTINCT(
        SELECTCOLUMNS(
            FILTER( ALL( 'Sales' ), 'Sales'[Date] < MIN( 'Calendar'[Date] ) ),
            "CustomerID", 'Sales'[CustomerID]
        )
    )
    RETURN EXCEPT( __Current, __Previous )
```

**Use for:**
- New vs returning customers
- Items added/removed
- Change detection

---

### INTERSECT - Rows in BOTH Tables

```dax
Returning Customers =
    VAR __Current = DISTINCT( 'Sales'[CustomerID] )
    VAR __Previous = DISTINCT(
        SELECTCOLUMNS(
            FILTER( ALL( 'Sales' ), [Date] < MIN( 'Calendar'[Date] ) ),
            "CustomerID", 'Sales'[CustomerID]
        )
    )
    RETURN INTERSECT( __Current, __Previous )
```

---

### NATURALINNERJOIN / NATURALLEFTOUTERJOIN

Join tables by matching column names:

```dax
Joined =
    NATURALINNERJOIN(
        SELECTCOLUMNS( 'Sales', "ID", [ProductID], "Amount", [Amount] ),
        SELECTCOLUMNS( 'Products', "ID", [ProductID], "Name", [ProductName] )
    )
```

> [!WARNING]
> Use sparingly. Explicit column matching is clearer.

---


### IN Operator Uses (Quick Examples)

**Basic List Filter:**
```dax
High Priority Colors =
    VAR __Table = FILTER(
        'Sales',
        'Sales'[Color] IN { "Red", "Yellow", "Orange" }
    )
    RETURN SUMX( __Table, [Amount] )
```

### IN with Table

```dax
Top Customers =
    VAR __Top10 = TOPN( 10, ALL( 'Customer' ), [Total Sales], DESC )
    VAR __Table = FILTER(
        'Sales',
        'Sales'[CustomerID] IN __Top10
    )
    RETURN SUMX( __Table, [Amount] )
```

### NOT IN Pattern

```dax
Exclude Items =
    VAR __Exclusions = { "Pickle", "Banana" }
    VAR __Table = FILTER(
        'Sales',
        NOT( 'Sales'[Item] IN __Exclusions )
    )
    RETURN SUMX( __Table, [Amount] )
```

---

## CONTAINSROW - Check Row Existence

Check if a specific row exists in a table:

```dax
Has Red Electronics =
    VAR __Check = CONTAINSROW(
        'Sales',
        "Red",      -- Color column
        "Electronics"  -- Category column
    )
    RETURN __Check  -- Returns TRUE/FALSE
```

**vs IN:**
- IN: Check column value in set
- CONTAINSROW: Check entire row combination exists

---

## Performance Comparison

| Function | Performance | Use When |
|----------|------------|----------|
| GROUPBY | ⚡⚡⚡ Fast | Single table grouping |
| SUMMARIZE | ⚡⚡ Medium | Cross-table grouping |
| SUMMARIZECOLUMNS | ⚡⚡⚡ Fast | DAX queries only |
| FILTER | ⚡⚡ Medium | Always (fundamental) |
| ADDCOLUMNS | ⚡⚡ Medium | Adding calculations |
| SELECTCOLUMNS | ⚡⚡⚡ Fast | Reducing table width |

---

## Common Patterns

### Pattern: Filter → Add Columns → Aggregate

```dax
Complex Calculation =
    VAR __Filtered = FILTER( 'Sales', 'Sales'[Region] = "North" )
    VAR __Enhanced = ADDCOLUMNS(
        __Filtered,
        "__Profit", [Revenue] - [Cost],
        "__Margin", DIVIDE( [Revenue] - [Cost], [Revenue], 0 )
    )
    VAR __Result = AVERAGEX( __Enhanced, [__Margin] )
    RETURN __Result
```

### Pattern: Group → Filter Groups → Aggregate

```dax
High Volume Customers =
    VAR __Grouped = SUMMARIZE(
        'Sales',
        'Sales'[CustomerID],
        "__Orders", COUNTROWS( 'Sales' ),
        "__Total", SUM( 'Sales'[Amount] )
    )
    VAR __HighVolume = FILTER( __Grouped, [__Orders] > 10 )
    VAR __Result = COUNTROWS( __HighVolume )
    RETURN __Result
```

### Pattern: Set Operations for Change Detection

```dax
Lost Customers =
    VAR __LastMonth = DISTINCT( SELECTCOLUMNS(
        FILTER( ALL( 'Sales' ), [Date] >= EOMONTH( TODAY(), -2 ) + 1 && [Date] <= EOMONTH( TODAY(), -1 ) ),
        "ID", [CustomerID]
    ))
    VAR __ThisMonth = DISTINCT( 'Sales'[CustomerID] )
    RETURN COUNTROWS( EXCEPT( __LastMonth, __ThisMonth ) )
```

---

## Debugging Table Functions

For comprehensive debugging techniques including `TOCSV`, `COUNTROWS`, and step-by-step variable inspection, see [Debugging Techniques](./debugging.md).

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| `SUMMARIZE` in measures with filters | Unexpected results | Use SUMMARIZE in VAR, then filter the result |
| Forgetting CURRENTGROUP() in GROUPBY | Aggregation errors | Always use CURRENTGROUP() for aggregations |
| UNION with mismatched columns | Error | Ensure same column count and types |
| Using VALUES expecting DISTINCT | BLANK appears unexpectedly | Use DISTINCT when you don't want BLANK |
| ADDCOLUMNS without intermediate VAR | Hard to debug | Always assign ADDCOLUMNS to VAR |

---

## See Also

- [Function Reference](function-reference.md) - ALL, ALLSELECTED, HASONEVALUE details
- [Advanced & Complex Patterns](advanced-complex-patterns.md) - Complex table operations
- [Performance Reference](performance-reference.md) - Optimization techniques
