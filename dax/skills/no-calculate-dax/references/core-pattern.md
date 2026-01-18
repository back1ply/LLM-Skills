# Core Pattern & Standard Measures

Detailed patterns for the No CALCULATE methodology.

## Standard Measure Template

```dax
Measure Name = 
    VAR __ValueToFilter = "Red"
    VAR __Table = FILTER( 'Sales', 'Sales'[Color] = __ValueToFilter )
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result
```

## Calculating Ratios (Safe Division)

```dax
Gross Margin % = 
    VAR __Revenue = SUMX( 'Sales', [Quantity] * [Price] )
    VAR __Cost = SUMX( 'Sales', [Quantity] * [Cost] )
    VAR __Margin = __Revenue - __Cost
    VAR __Result = DIVIDE( __Margin, __Revenue, 0 )
    RETURN __Result
```

## Lookup Alternative

Use `MAXX` + `FILTER` instead of `LOOKUPVALUE` (more reliable):

```dax
Lookup Value = 
    VAR __KeyValue = MAX( 'Table'[Key] )
    VAR __Table = FILTER( 'LookupTable', 'LookupTable'[Key] = __KeyValue )
    VAR __Result = MAXX( __Table, 'LookupTable'[TargetColumn] )
    RETURN __Result
```

## Multiple Filters

Use logical operators for complex filtering:

```dax
Filtered Measure = 
    VAR __Table = FILTER( 
        'Sales', 
        'Sales'[Category] = "Electronics" && 'Sales'[Region] = "North"
    )
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result
```

**Logical Operators:**

- `&&` = AND
- `||` = OR
- `<>` = NOT EQUAL

## Double Lookup Pattern

Look up a value based on another lookup:

```dax
Double Lookup = 
    VAR __MaxDate = MAX( 'Table'[Date] )
    VAR __Table = FILTER( 'Table', 'Table'[Date] = __MaxDate )
    VAR __Result = MAXX( __Table, [Total Cost] )
    RETURN __Result
```

## Optimization Tips

- Filter early and filter often to reduce table sizes
- Use `SWITCH( TRUE(), ... )` instead of nested `IF` statements
- Avoid `VALUE` and `VALUES` when `DISTINCT` will suffice

## When User Provides CALCULATE Code

Refactor it to the linear, readable format:

1. Identify what CALCULATE is filtering
2. Replace with explicit `FILTER` + table variable
3. Use X-aggregator over the filtered table
4. Ensure all context is explicitly visible
