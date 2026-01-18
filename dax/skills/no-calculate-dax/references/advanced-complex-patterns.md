# Advanced & Complex Patterns

Complex DAX patterns for advanced scenarios including disconnected tables, simulating loops, multi-table operations, and mathematical workarounds.

> **See Also:** For philosophy and core tenets, see [Philosophy](./philosophy.md). For the variable pattern, see [Core Pattern](./core-pattern.md). For CALCULATE guidance, see [Function Reference](./function-reference.md#when-calculate-is-acceptable).

---

## Disconnected Tables

For "Not Slicers", "And Slicers", or parameter tables with no model relationship. Create the relationship virtually in DAX:

```dax
Sales by Parameter = 
    VAR __Selection = MAX( 'ParameterTable'[Value] )
    VAR __Table = FILTER( 'Sales', 'Sales'[Category] = __Selection )
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result
```

### Multi-Select Parameter

```dax
Sales by Multi-Select = 
    VAR __Selections = VALUES( 'ParameterTable'[Value] )
    VAR __Table = FILTER( 'Sales', 'Sales'[Category] IN __Selections )
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result
```

---

## Text-to-Table Parsing

> **See**: [Text Patterns](./text-patterns.md#text-to-table) for patterns on parsing delimited strings into tables.


---

## Simulating Loops

DAX lacks loops. Use `GENERATESERIES` + `ADDCOLUMNS` for iteration:

```dax
Running Total = 
    VAR __MaxRow = COUNTROWS( 'Table' )
    VAR __Table = ADDCOLUMNS(
        GENERATESERIES( 1, __MaxRow ),
        "__RunningSum", 
        SUMX( 
            FILTER( 'Table', 'Table'[RowNum] <= [Value] ), 
            [Amount] 
        )
    )
    VAR __Result = MAXX( __Table, [__RunningSum] )
    RETURN __Result
```

---

## Math & Function Workarounds

### Better MOD (handles decimals)

Standard `MOD` is buggy with decimals:

```dax
Better MOD = 
    VAR __Dividend = [Value]
    VAR __Divisor = 3
    RETURN __Dividend - TRUNC( __Dividend / __Divisor ) * __Divisor
```

### Better MEDIAN (for calculated columns)

```dax
Median Value = CONVERT( MEDIAN( 'Table'[Value] ), DOUBLE )
```

Or use MEDIANX:

```dax
Median Value = MEDIANX( 'Table', [Value] )
```

### ATAN2 (not native in DAX)

See [Distance & Space Patterns](distance-space-patterns.md#atan2-implementation) for the full ATAN2 implementation.

---

## NOT Slicer

Show all items EXCEPT what's selected:

```dax
NOT Slicer Measure = 
    VAR __Selected = VALUES( 'Slicer'[Category] )
    VAR __Table = FILTER( 'Sales', NOT( 'Sales'[Category] IN __Selected ) )
    RETURN SUMX( __Table, [Amount] )
```

---

## AND Slicer

Require ALL selected values (not any):

```dax
AND Slicer Measure = 
    VAR __SelectionCount = COUNTROWS( VALUES( 'Slicer'[Tag] ) )
    VAR __Table = FILTER(
        SUMMARIZE( 'Sales', 'Sales'[ProductID], "__TagCount", 
            COUNTROWS( INTERSECT( VALUES( 'Sales'[Tag] ), VALUES( 'Slicer'[Tag] ) ) )
        ),
        [__TagCount] = __SelectionCount
    )
    RETURN SUMX( __Table, [Amount] )
```

---




---

## Multi-Table Operations (Advanced Examples)

For basic UNION, EXCEPT, INTERSECT, and CROSSJOIN syntax, see Table Functions Reference.

### EXCEPT: Find Churned Customers

```dax
Churned Customers = 
    VAR __LastPeriod = SELECTCOLUMNS( 
        FILTER( ALL('Sales'), 'Sales'[Year] = 2023 ), "ID", 'Sales'[CustomerID] )
    VAR __ThisPeriod = SELECTCOLUMNS( 
        FILTER( ALL('Sales'), 'Sales'[Year] = 2024 ), "ID", 'Sales'[CustomerID] )
    RETURN COUNTROWS( EXCEPT( DISTINCT(__LastPeriod), DISTINCT(__ThisPeriod) ) )
```

### INTERSECT: Products Sold in ALL Regions

```dax
Products in All Regions = 
    VAR __Regions = DISTINCT( 'Geography'[Region] )
    VAR __RegionCount = COUNTROWS( __Regions )
    VAR __ProductRegions = SUMMARIZE( 'Sales', [ProductID], [Region] )
    VAR __ProductCounts = SUMMARIZE( __ProductRegions, [ProductID], 
        "__RegionCount", COUNTROWS( __ProductRegions ) )
    RETURN COUNTROWS( FILTER( __ProductCounts, [__RegionCount] = __RegionCount ) )
```

### CROSSJOIN: Budget Matrix Template

```dax
Budget Template = 
    VAR __Months = DISTINCT( 'Calendar'[YearMonth] )
    VAR __Departments = DISTINCT( 'Departments'[Department] )
    VAR __Accounts = DISTINCT( 'ChartOfAccounts'[Account] )
    RETURN CROSSJOIN( __Months, __Departments, __Accounts )
```
> [!WARNING]
> CROSSJOIN can create very large tables. Only use with small dimension tables.

---

## Complex Selector Pattern

Embed complex selection logic into a measure, then use it in the Filters pane:

```dax
Selector = 
    VAR __Item = MAX( 'Table'[Item] )
    VAR __Cost = SUM( 'Table'[Total Cost] )
    VAR __Result = IF( 
        ( __Item = "Pickle" || __Item = "Grapefruit" ) && __Cost > 10,
        1,
        0 
    )
    RETURN __Result
```

**Usage**: Add this measure to visual, then filter `Selector = 1` in the Filters pane.

### Multiple Condition Logic

For multiple complex conditions, use `SWITCH(TRUE)`:

```dax
Customer Segment = 
    VAR __Revenue = [Total Revenue]
    VAR __Orders = [Order Count]
    VAR __Recency = [Days Since Last Order]
    RETURN SWITCH(
        TRUE(),
        __Revenue > 10000 && __Recency < 30, 1,        -- VIP Active
        __Revenue > 10000 && __Recency >= 30, 2,       -- VIP At Risk
        __Revenue > 1000 && __Recency < 90, 3,         -- Regular
        __Orders > 0, 4,                                -- Occasional
        0                                               -- Inactive
    )
```

---

## Custom Matrix Hierarchy

Override default Matrix visual behavior by using a disconnected hierarchy table for columns. Enables showing specific measures (like CY/LY) only in totals, not every cell.

### 1. Create the Hierarchy Table
This is best done in **Power Query** (see [Power Query Patterns](./power-query-patterns.md#custom-hierarchy-table)), but here is a DAX version using `DATATABLE` for quick testing.

```dax
Custom Hierarchy = 
    DATATABLE(
        "Header", STRING, "SubHeader", STRING, "Order", INTEGER,
        {
            { "2024", "January", 1 },
            { "2024", "February", 2 },
            { "2024", "March", 3 },
            { "Comparison", "vs Last Year", 4 },
            { "Comparison", "vs Budget", 5 }
        }
    )
```
Set Sort by column for Value2 to Value3.

### Complex Logic: The "Flag" Pattern

For very complex multi-step logic that is hard to express in a single FILTER, calculate a "Flag" variable first.

```dax
Complex Filter = 
    VAR __Table = 
        ADDCOLUMNS( 
            'Sales', 
            "__IsTarget", 
            SWITCH( TRUE(),
                [Type] = "A" && [Val] > 100, TRUE(),
                [Type] = "B" && [Val] > 200, TRUE(),
                FALSE()
            )
        )
    VAR __Result = SUMX( FILTER( __Table, [__IsTarget] = TRUE() ), [Amount] )
    RETURN __Result
```

### Step 2: Create Value Measure

```dax
Value to Show = 
    VAR __Level1 = MAX( 'Custom Hierarchy'[Value1] )
    VAR __Level2 = MAX( 'Custom Hierarchy'[Value2] )
    VAR __Order = MAX( 'Custom Hierarchy'[Value3] )
    
    RETURN SWITCH(
        TRUE(),
        __Level2 = "LY", [LY],
        __Level2 = "CY", [CY],
        __Level1 = "Total", SUM( 'Sales'[Total] ),
        ISINSCOPE( 'Custom Hierarchy'[Value2] ), 
            SUMX( FILTER( 'Sales', [MonthSort] = __Order && [Year] = __Level1 ), [Total] ),
        ISINSCOPE( 'Custom Hierarchy'[Value1] ), 
            SUMX( FILTER( 'Sales', [Year] = __Level1 ), [Total] ),
        BLANK()
    )
```

**Usage**: Use Custom Hierarchy columns for Matrix Columns and Value to Show for Values. CY/LY measures only appear in Total column, not every month.

---

## Dynamic Granularity Scale

View data at different levels of detail based on recency (e.g., weekly for current quarter, quarterly for past quarters, yearly for past years).

### Step 1: Create Calendar with DGS Column

```dax
Calendar = 
    VAR __Today = TODAY()
    VAR __CY = YEAR( __Today )
    VAR __CQ = QUARTER( __Today )
    
    VAR __Table = ADDCOLUMNS(
        ADDCOLUMNS(
            CALENDAR( DATE( 2023, 1, 1 ), TODAY() ),
            "IsCQ", IF( YEAR( [Date] ) = __CY && QUARTER( [Date] ) = __CQ, TRUE, FALSE )
        ),
        "DGS", SWITCH(
            TRUE(),
            [IsCQ], "W" & WEEKNUM( [Date] ) & " - " & YEAR( [Date] ),
            YEAR( [Date] ) = __CY, "Q" & QUARTER( [Date] ) & " - " & YEAR( [Date] ),
            YEAR( [Date] ) & ""
        ),
        "DGS Sort", SWITCH(
            TRUE(),
            [IsCQ], YEAR( [Date] ) * 1000 + QUARTER( [Date] ) * 100 + WEEKNUM( [Date] ),
            YEAR( [Date] ) = __CY, YEAR( [Date] ) * 1000 + QUARTER( [Date] ),
            YEAR( [Date] )
        )
    )
    RETURN __Table
```
Set Sort by column for DGS to DGS Sort.

### Step 2: Create Measure with Appropriate Aggregation

```dax
Weekly Inventory = 
    VAR __Table = SUMMARIZE(
        ADDCOLUMNS( 'Inventory',
            "__Year", YEAR( [Date] ),
            "__Quarter", QUARTER( [Date] ),
            "__Week", WEEKNUM( [Date] )
        ),
        [__Year], [__Quarter], [__Week],
        "__Value", SUM( 'Inventory'[Quantity] )
    )
    RETURN AVERAGEX( __Table, [__Value] )
```

**Use case**: Dashboards where recent data needs detail but historical data can be summarized.

---

## Overlap (Meeting Overlap)

> [!CAUTION]
> **Performance Warning**: The loop-based approach below (`GENERATE` every minute) is computationally expensive and suitable only for small datasets. For a much faster, math-based approach, see **[Time Duration Patterns: Net Work Duration](./time-duration-patterns.md#net-work-duration)**.

Calculate actual time in overlapping events (meetings, shifts, etc.):

```dax
Overlap Hours = 
    VAR __Start = MIN( 'Meetings'[Start] )
    VAR __End = MAX( 'Meetings'[End] )
    
    VAR __Table = GROUPBY(
        ADDCOLUMNS(
            GENERATE( 
                GENERATESERIES( __Start, __End, 1/24/60 ),  // Every minute
                ALL( 'Meetings' )
            ),
            "__Include", IF( [Value] >= [Start] && [Value] <= [End], 1, 0 )
        ),
        [Value],
        "__Minute", MAXX( CURRENTGROUP(), [__Include] )
    )
    
    VAR __Result = SUMX( __Table, [__Minute] ) / 60
    RETURN __Result
```

**Use case**: Calculate actual meeting time when multiple overlapping meetings exist.

---
---

## GAMMA Function (Lanczos Approximation)

DAX omits the GAMMA function. Use the Lanczos approximation for a numerical solution (accurate to 12-13 decimal places).

```dax
GAMMA = 
    VAR __zInput = MAX( 'z'[Value] ) 
    VAR __Result = IF( 
        __zInput = TRUNC( __zInput ), 
        FACT( __zInput - 1 ), 
        VAR __p = { 
            ( 0, 676.5203681218851 ), ( 1, -1259.1392167224028 ), 
            ( 2, 771.32342877765313 ), ( 3, -176.61502916214059 ), 
            ( 4, 12.507343278686905 ), ( 5, -0.13857109526572012 ), 
            ( 6, 9.9843695780195716e-6 ), ( 7, 1.5056327351493116e-7 ) 
        } 
        VAR __z = IF( __zInput < 0.5, 1 - __zInput - 1, __zInput - 1 ) 
        VAR __pTable = ADDCOLUMNS( __p, "x", [Value2] / ( __z + [Value1] + 1 ) ) 
        VAR __x = 0.99999999999980993 + SUMX( __pTable, [x] ) 
        VAR __t = __z + COUNTROWS( __pTable ) - .5 
        VAR __y = IF( 
            __zInput < 0.5, 
            PI() / ( SIN( PI() * __zInput ) * SQRT( 2 * PI()) * POWER( __t, __z + 0.5 ) * EXP( -1 * __t ) * __x ), 
            SQRT( 2 * PI() ) * POWER( __t, __z + 0.5 ) * EXP( -1 * __t ) * __x 
        ) 
        RETURN __y 
    ) 
    RETURN __Result
```

---

## DAX Index

Generating a sorted index within a DAX measure or calculated table using `CONCATENATEX` and `PATHITEM`.

### Simple Sorted Index

```dax
DAX Index Sorted Table = 
    VAR __Table = 'Index' 
    VAR __Path = CONCATENATEX( __Table, [Product], "|", [Product], ASC ) 
    VAR __Result = ADDCOLUMNS( 
        SELECTCOLUMNS( GENERATESERIES( 1, COUNTROWS( __Table ), 1 ), "Index", [Value] ), 
        "Product", PATHITEM( __Path, [Index] ) 
    ) 
    RETURN __Result
```

### Multi-Column Index with Parsing

```dax
DAX Index Multi-Column = 
    VAR __Table = ADDCOLUMNS( 'Index', "Value", [Sales] ) 
    VAR __Path = CONCATENATEX( __Table, [Product] & "~" & [Value], "|", [Value], DESC ) 
    VAR __Result = ADDCOLUMNS( 
        SELECTCOLUMNS( GENERATESERIES( 1, COUNTROWS( __Table ), 1 ), "Index", [Value] ), 
        "Product", 
            VAR __Item = PATHITEM( __Path, [Index] ) 
            RETURN MID( __Item, 1, FIND( "~", __Item ) - 1 ), 
        "Value", 
            VAR __Item = PATHITEM( __Path, [Index] ) 
            RETURN MID( __Item, FIND( "~", __Item ) + 1, LEN( __Item ) - FIND( "~", __Item ) ) 
    ) 
    RETURN __Result
```

---

## Streaks (Consecutive Occurrences)

Calculate an index that increments for consecutive rows in the same group and restarts when the group changes.

### Bride of Cthulhu Pattern

Works even with non-consecutive Index/Date columns:

```dax
Streak Count = 
    VAR __CurrentIndex = MAX ( 'Streaks'[Index] ) 
    VAR __CurrentGroup = MAX ( 'Streaks'[Animal] ) 
    VAR __StreakStart = MAXX ( 
        FILTER( ALL( 'Streaks' ), [Index] < __CurrentIndex && [Animal] <> __CurrentGroup ), 
        [Index] 
    ) 
    VAR __LocalGroupCount = COUNTROWS( 
        FILTER( ALL( 'Streaks' ), [Index] <= __CurrentIndex && [Index] > __StreakStart ) 
    ) 
    VAR __Result = __LocalGroupCount 
    RETURN __Result
```

### Longest Streak

```dax
Longest Streak = 
    VAR __Table = ADDCOLUMNS( 'Streaks', 
        "__Streak", 
        VAR __CurrentIndex = [Index] 
        VAR __CurrentGroup = [Animal] 
        VAR __StreakStart = MAXX ( 
            FILTER( ALL( 'Streaks' ), [Index] < __CurrentIndex && [Animal] <> __CurrentGroup ), 
            [Index] 
        ) 
        RETURN COUNTROWS( 
            FILTER( ALL( 'Streaks' ), [Index] <= __CurrentIndex && [Index] > __StreakStart ) 
        ) 
    ) 
    VAR __Result = IF( 
        HASONEVALUE( 'Streaks'[Animal] ), 
        MAXX( __Table, [__Streak] ) & "", 
        MAXX( FILTER( __Table, [__Streak] = MAXX( __Table, [__Streak] ) ), [Animal] ) 
    ) 
    RETURN __Result
```

---

## Multi-Column Aggregations

Aggregating data across multiple columns without unpivoting in Power Query.

### Brute Force Sum (for narrow tables)

```dax
Multi-Column Sum = 
    VAR __Table = UNION( 
        SELECTCOLUMNS( 'Table', "__Value", [Jan] ), 
        SELECTCOLUMNS( 'Table', "__Value", [Feb] ), 
        SELECTCOLUMNS( 'Table', "__Value", [Mar] ) 
    ) 
    VAR __Result = SUMX( __Table, [__Value] ) 
    RETURN __Result
```

### Dynamic Multi-Column Average (for wide tables)

Uses `TOCSV` to parse wide tables dynamically:

```dax
Wide MC Average = 
    VAR __TableWHeaders = SUBSTITUTE( TOCSV( 'Wide', , ",", 1 ), UNICHAR( 10 ) , "|") 
    VAR __Headers = PATHITEM( __TableWHeaders, 1 ) 
    VAR __FirstColon = FIND( ":", __Headers ) 
    VAR __Left = LEFT( __Headers, __FirstColon ) 
    VAR __Commas = LEN( __Left ) - LEN( SUBSTITUTE( __Left, ",", "" ) ) 
    VAR __TableWOHeaders = SUBSTITUTE( TOCSV( 'Wide', , ",", 0 ), UNICHAR( 10 ), "|") 
    VAR __Count = COUNTROWS( 'Wide' ) 
    VAR __Data = ADDCOLUMNS( 
        GENERATESERIES( 1, __Count, 1 ), 
        "__Data", 
        VAR __Text = PATHITEM( __TableWOHeaders, [Value] ) 
        VAR __Path = SUBSTITUTE( __Text, ",", "|", __Commas ) 
        VAR __Result = PATHITEM( __Path, 2 ) 
        RETURN __Result 
    ) 
    VAR __DataText = CONCATENATEX( __Data, [__Data], "|" ) 
    VAR __Path = SUBSTITUTE( __DataText, ",", "|" ) 
    VAR __DataColumns = LEN( __DataText) - LEN( SUBSTITUTE( __DataText, ",", "" ) ) 
    VAR __Table = ADDCOLUMNS( 
        GENERATESERIES(1, __DataColumns, 1 ), 
        "__Value", PATHITEM( __Path, [Value] ) + 0 
    ) 
    VAR __Result = AVERAGEX( __Table, [__Value] ) 
    RETURN __Result
```
