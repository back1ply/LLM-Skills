# Number Patterns

Numeric functions and statistical patterns using the No CALCULATE approach.

---

## Safe Division

Always use DIVIDE instead of `/` to prevent divide-by-zero errors:

```dax
Safe Ratio = 
    VAR __Numerator = SUM( 'Sales'[Amount] )
    VAR __Denominator = SUM( 'Sales'[Quantity] )
    VAR __Result = DIVIDE( __Numerator, __Denominator, 0 )
    RETURN __Result
```

The third parameter is the alternate result when denominator is 0 or BLANK.

---

## Rounding Functions

```dax
// Round to nearest integer
Rounded = ROUND( [Value], 0 )

// Round to 2 decimal places
Rounded 2dp = ROUND( [Value], 2 )

// Always round up
Ceiling = ROUNDUP( [Value], 0 )

// Always round down
Floor = ROUNDDOWN( [Value], 0 )

// Truncate (remove decimals, preserves sign correctly for negatives)
Truncated = TRUNC( [Value] )

// Integer portion (NOTE: INT(-2.1) = -3, use TRUNC for negatives)
Integer = INT( [Value] )

// Round to nearest multiple
To Nearest 5 = MROUND( [Value], 5 )

// Ceiling to multiple
Ceiling 100 = CEILING( [Value], 100 )

// Floor to multiple
Floor 100 = FLOOR( [Value], 100 )
```

> **Tip**: Use `TRUNC` instead of `INT` when working with negative numbers.

---

## Statistical Aggregations

```dax
// Standard aggregations
Sum = SUMX( 'Table', [Value] )
Average = AVERAGEX( 'Table', [Value] )
Minimum = MINX( 'Table', [Value] )
Maximum = MAXX( 'Table', [Value] )
Count = COUNTX( 'Table', [Value] )

// Standard deviation (population)
StdDev = STDEVX.P( 'Table', [Value] )

// Standard deviation (sample)  
StdDev Sample = STDEVX.S( 'Table', [Value] )

// Variance (population)
Variance = VARX.P( 'Table', [Value] )

// Variance (sample)
Variance Sample = VARX.S( 'Table', [Value] )

// Median
Median = MEDIANX( 'Table', [Value] )

// Percentile (inclusive - includes exact boundaries)
P90 = PERCENTILEX.INC( 'Table', [Value], 0.90 )

// Percentile (exclusive - excludes exact boundaries)
P90 Exclusive = PERCENTILEX.EXC( 'Table', [Value], 0.90 )

// Quartiles
Q1 = PERCENTILEX.INC( 'Table', [Value], 0.25 )
Q3 = PERCENTILEX.INC( 'Table', [Value], 0.75 )
IQR = PERCENTILEX.INC( 'Table', [Value], 0.75 ) - PERCENTILEX.INC( 'Table', [Value], 0.25 )
```

---

## Aggregating Measures

Aggregate measure values across a different context than they were calculated:

### Sum of Measure Values

```dax
Sum of Measure = 
    VAR __Table = SUMMARIZE( 
        'Sales', 
        'Sales'[Category],
        "__MeasureValue", [Base Measure]
    )
    VAR __Result = SUMX( __Table, [__MeasureValue] )
    RETURN __Result
```

### Average of Measure Values

```dax
Average of Measure = 
    VAR __Table = SUMMARIZE( 
        'Sales', 
        'Sales'[Category],
        "__MeasureValue", [Base Measure]
    )
    VAR __Result = AVERAGEX( __Table, [__MeasureValue] )
    RETURN __Result
```

### Max/Min of Measure Values

```dax
Max Measure = 
    VAR __Table = SUMMARIZE( 
        'Products', 
        [ProductID],
        "__Value", [Margin %]
    )
    RETURN MAXX( __Table, [__Value] )

Min Measure = 
    VAR __Table = SUMMARIZE( 
        'Products', 
        [ProductID],
        "__Value", [Margin %]
    )
    RETURN MINX( __Table, [__Value] )
```

> **Key Pattern**: Use SUMMARIZE to create a table at the desired granularity, then aggregate with SUMX/AVERAGEX/MAXX/MINX.

---

## Number Formatting

For comprehensive number, date, and currency formatting, see [FORMAT Reference](format-reference.md).

Quick examples:
```dax
// Currency
FORMAT( [Value], "$#,##0.00" )           → "$1,234.50"

// Percentage
FORMAT( [Rate], "0.0%" )                 → "15.6%"

// Thousands with K suffix
FORMAT( [Value] / 1000, "#,##0" ) & "K"  → "1,235K"

// Millions with M suffix
FORMAT( [Value] / 1000000, "#,##0.0" ) & "M"  → "1.2M"
```

See [FORMAT Reference](format-reference.md) for complete documentation.

---

## Mode (Most Frequent Value)

Find the most frequently occurring value:

```dax
Mode = 
    VAR __Counts = GROUPBY(
        'Data',
        [Value],
        "__Count", COUNTROWS( CURRENTGROUP() )
    )
    VAR __MaxCount = MAXX( __Counts, [__Count] )
    VAR __Modes = FILTER( __Counts, [__Count] = __MaxCount )
    VAR __Result = MINX( __Modes, [Value] )  -- Return lowest if tie
    RETURN __Result
```

With tie detection:

```dax
Mode With Ties = 
    VAR __Counts = GROUPBY(
        'Data',
        [Value],
        "__Count", COUNTROWS( CURRENTGROUP() )
    )
    VAR __MaxCount = MAXX( __Counts, [__Count] )
    VAR __Modes = FILTER( __Counts, [__Count] = __MaxCount )
    VAR __ModeCount = COUNTROWS( __Modes )
    VAR __Result = IF(
        __ModeCount = 1,
        FORMAT( MINX( __Modes, [Value] ), "0" ),
        "Multiple modes (" & __ModeCount & ")"
    )
    RETURN __Result
```

All modes as comma-separated list:

```dax
All Modes = 
    VAR __Counts = GROUPBY(
        'Data',
        [Value],
        "__Count", COUNTROWS( CURRENTGROUP() )
    )
    VAR __MaxCount = MAXX( __Counts, [__Count] )
    VAR __Modes = FILTER( __Counts, [__Count] = __MaxCount )
    VAR __Result = CONCATENATEX( __Modes, [Value], ", ", [Value] )
    RETURN __Result
```

---

## Weighted Average

```dax
Weighted Average = 
    VAR __Table = ADDCOLUMNS(
        'Sales',
        "__Weighted", [Price] * [Quantity]
    )
    VAR __TotalWeight = SUMX( __Table, [Quantity] )
    VAR __WeightedSum = SUMX( __Table, [__Weighted] )
    VAR __Result = DIVIDE( __WeightedSum, __TotalWeight )
    RETURN __Result
```

---

## Ranking

Basic rank (with gaps for ties):
```dax
Rank = 
    VAR __CurrentValue = MAX( 'Products'[Sales] )
    VAR __Table = ALL( 'Products' )
    VAR __Result = COUNTROWS( 
        FILTER( __Table, [Sales] > __CurrentValue ) 
    ) + 1
    RETURN __Result
```

Dense rank (no gaps):
```dax
Dense Rank = 
    VAR __CurrentValue = MAX( 'Products'[Sales] )
    VAR __DistinctValues = DISTINCT( ALL( 'Products'[Sales] ) )
    VAR __Result = COUNTROWS( 
        FILTER( __DistinctValues, [Sales] > __CurrentValue ) 
    ) + 1
    RETURN __Result
```

Using RANKX (for calculated columns):
```dax
Rank Column = 
    RANKX( 
        ALL( 'Products' ), 
        [Sales], 
        , 
        DESC, 
        DENSE 
    )
```

---

## Percentile / Trimmed Mean

Trimmed mean (exclude top/bottom 10%):
```dax
Trimmed Mean = 
    VAR __Table = ALL( 'Table' )
    VAR __Sorted = ADDCOLUMNS(
        __Table,
        "__Rank", RANKX( __Table, [Value], , ASC, DENSE )
    )
    VAR __Count = COUNTROWS( __Table )
    VAR __TrimCount = ROUND( __Count * 0.1, 0 )
    VAR __Trimmed = FILTER( 
        __Sorted, 
        [__Rank] > __TrimCount && [__Rank] <= __Count - __TrimCount 
    )
    VAR __Result = AVERAGEX( __Trimmed, [Value] )
    RETURN __Result
```

## Linear Interpolation

> [!NOTE]
> This is a **simple point-to-point interpolation** between two known X values. For **gap-filling** across multiple missing data points in a time series, see [Statistics Patterns: Linear Interpolation](./statistics-patterns.md#linear-interpolation).

Estimate a value between two known points:

```dax
Interpolated = 
    VAR __TargetX = [Target X Value]
    VAR __Table = 'DataPoints'
    VAR __LowerRow = TOPN( 1, FILTER( __Table, [X] <= __TargetX ), [X], DESC )
    VAR __UpperRow = TOPN( 1, FILTER( __Table, [X] >= __TargetX ), [X], ASC )
    VAR __X1 = MINX( __LowerRow, [X] )
    VAR __Y1 = MINX( __LowerRow, [Y] )
    VAR __X2 = MINX( __UpperRow, [X] )
    VAR __Y2 = MINX( __UpperRow, [Y] )
    VAR __Slope = DIVIDE( __Y2 - __Y1, __X2 - __X1, 0 )
    VAR __Result = __Y1 + __Slope * ( __TargetX - __X1 )
    RETURN __Result
```

---

## Linear Regression & Advanced Statistics

For regression analysis, correlation, z-scores, and advanced statistical patterns, see [Statistics Patterns](statistics-patterns.md).

Topics covered in statistics-patterns.md:
- Linear regression (slope, intercept, R-squared)
- Correlation (Pearson coefficient)
- Percentiles & quartiles (custom implementation)
- Standard deviation, variance, z-scores
- Confidence intervals
- Exponential smoothing
- Statistical tests & forecasting

---

## Operators Reference

| Operator | Purpose | Example |
|----------|---------|---------|
| `+` | Addition | `5 + 3` → 8 |
| `-` | Subtraction | `5 - 3` → 2 |
| `*` | Multiplication | `5 * 3` → 15 |
| `/` | Division (use DIVIDE instead) | `6 / 3` → 2 |
| `^` | Exponentiation | `2 ^ 3` → 8 |
| `=` | Equals (0 = BLANK is TRUE) | Comparison |
| `==` | Strict equals (0 == BLANK is FALSE) | Strict comparison |
| `<>` | Not equals | Comparison |
