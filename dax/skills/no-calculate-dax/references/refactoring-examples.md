# Refactoring Examples (Before vs After)

Common scenarios for converting standard DAX (using `CALCULATE`) to the No CALCULATE methodology.

## 1. Simple Filter

**Scenario:** Calculate Sales for "Red" products.

### ❌ Before (Standard)
```dax
Red Sales = CALCULATE( SUM( 'Sales'[Amount] ), 'Product'[Color] = "Red" )
```

### ✅ After (No CALCULATE)
```dax
Red Sales = 
    VAR __FilterValue = "Red"
    VAR __Table = FILTER( 'Sales', RELATED( 'Product'[Color] ) = __FilterValue )
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result
```

---

## 2. Percent of Total (ALL)

**Scenario:** Sales as a % of all colors.

> **See also**: [Function Reference: % of Total Patterns](./function-reference.md#-of-total-patterns) for additional variations using ALL vs ALLSELECTED.

### ❌ Before (Standard)
```dax
% of All Sales = 
    DIVIDE( 
        SUM( 'Sales'[Amount] ),
        CALCULATE( SUM( 'Sales'[Amount] ), ALL( 'Sales' ) )
    )
```

### ✅ After (No CALCULATE)
```dax
% of All Sales = 
    VAR __TotalSales = SUMX( 'Sales', [Amount] )
    VAR __AllSales = SUMX( ALL( 'Sales' ), [Amount] )
    VAR __Result = DIVIDE( __TotalSales, __AllSales, 0 )
    RETURN __Result
```

*Note: `ALL('Sales')` returns the entire table ignoring filters. We iterate (`SUMX`) over that unfiltered table.*

---

## 3. Time Intelligence (YTD)

**Scenario:** Year-to-Date calculation.

### ❌ Before (Standard)
```dax
Sales YTD = TOTALYTD( SUM( 'Sales'[Amount] ), 'Calendar'[Date] )
```

### ✅ After (No CALCULATE)
```dax
Sales YTD = 
    VAR __Today = MAX( 'Calendar'[Date] )
    VAR __CurrentYearOffset = MAX( 'Calendar'[CurrYearOffset] )
    VAR __Table = SUMMARIZE(
        FILTER( 
            ALL( 'Calendar' ), 
            'Calendar'[Date] <= __Today && 
            'Calendar'[CurrYearOffset] = __CurrentYearOffset
        ),
        'Calendar'[Date],
        "__Value", SUM( 'Sales'[Amount] )
    )
    VAR __Result = SUMX( __Table, [__Value] )
    RETURN __Result
```

---

## 4. Time Intelligence (Previous Year)

**Scenario:** Sales for the same period last year.

### ❌ Before (Standard)
```dax
Sales PY = CALCULATE( SUM( 'Sales'[Amount] ), SAMEPERIODLASTYEAR( 'Calendar'[Date] ) )
```

### ✅ After (No CALCULATE)
```dax
Sales PY = 
    VAR __PrevYearOffset = MAX( 'Calendar'[CurrYearOffset] ) - 1
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), 'Calendar'[CurrYearOffset] = __PrevYearOffset ),
        'Calendar'[Date],
        "__Value", SUM( 'Sales'[Amount] )
    )
    VAR __Result = SUMX( __Table, [__Value] )
    RETURN __Result
```

---

## 5. CALCULATETABLE logic

**Scenario:** Creating a virtual table for iteration.

### ❌ Before (Standard)
```dax
High Value Sales = 
    VAR __Table = CALCULATETABLE( 'Sales', 'Sales'[Amount] > 100 )
    RETURN COUNTROWS( __Table )
```

### ✅ After (No CALCULATE)
```dax
High Value Sales = 
    VAR __Table = FILTER( 'Sales', 'Sales'[Amount] > 100 )
    RETURN COUNTROWS( __Table )
```

*Note: `FILTER` is literally the replacement for `CALCULATETABLE` when you just need to reduce rows.*

---

## 6. USERELATIONSHIP

**Scenario:** Activating an inactive relationship (e.g., Ship Date).

### ❌ Before (Standard)
```dax
Shipped Sales = 
    CALCULATE( 
        SUM( 'Sales'[Amount] ), 
        USERELATIONSHIP( 'Sales'[ShipDate], 'Calendar'[Date] )
    )
```

### ✅ After (No CALCULATE)
```dax
Shipped Sales = 
    -- 1. Get the list of selected dates from the Calendar (Filter Context)
    VAR __Dates = VALUES( 'Calendar'[Date] )
    
    -- 2. Filter the Fact table explicitly using TREATAS or explicit logic
    VAR __Table = FILTER( 
        'Sales', 
        'Sales'[ShipDate] IN __Dates 
    )
    
    -- 3. Aggregation
    VAR __Result = SUMX( __Table, [Amount] )
    RETURN __Result
```

*Note: This is one of the few areas where `CALCULATE` + `USERELATIONSHIP` is significantly more performant/convenient. However, the explicit filter pattern above adheres to the strict methodology.*

---

## 7. Complex "KEEPFILTERS"

**Scenario:** Adding a filter without removing existing ones on the same column.

### ❌ Before (Standard)
```dax
Red Sales (Keep) = CALCULATE( [Total Sales], KEEPFILTERS( 'Product'[Color] = "Red" ) )
```

### ✅ After (No CALCULATE)
```dax
Red Sales (Keep) = 
    VAR __CurrentContext = VALUES( 'Product'[Color] ) -- See what's currently selected
    VAR __Table = FILTER( 
        'Product', 
        'Product'[Color] = "Red" && 'Product'[Color] IN __CurrentContext 
    )
    VAR __Result = SUMX( FILTER( 'Sales', RELATED('Product'[Color]) IN __Table ), [Amount] )
    RETURN __Result
```

---

## Quick Migration Reference (Rosetta Stone)

Map standard DAX functions to their "No CALCULATE" equivalents.

### Time Intelligence

| Standard Function | No-CALCULATE Equivalent Pattern |
| :--- | :--- |
| **`TOTALYTD( [Meas], 'Date'[Date] )`** | `FILTER( ALL('Date'), 'Date'[YearOffset] = 0 && 'Date'[Date] <= MAX('Date'[Date]) )` |
| **`SAMEPERIODLASTYEAR( 'Date'[Date] )`** | `FILTER( ALL('Date'), 'Date'[YearOffset] = -1 )` |
| **`DATESINPERIOD( ..., -6, MONTH )`** | `FILTER( ALL('Date'), 'Date'[MonthOffset] >= -5 && 'Date'[MonthOffset] <= 0 )` |
| **`PARALLELPERIOD( ..., -1, YEAR )`** | `FILTER( ALL('Date'), 'Date'[YearOffset] = -1 )` |
| **`PREVIOUSMONTH( 'Date'[Date] )`** | `FILTER( ALL('Date'), 'Date'[MonthOffset] = -1 )` |

### Filtering

| Standard Function | No-CALCULATE Equivalent Pattern |
| :--- | :--- |
| **`CALCULATE( [Meas], 'T'[C] = "A" )`** | `VAR __Table = FILTER( 'T', 'T'[C] = "A" ) RETURN SUMX( __Table, [Meas] )` |
| **`FILTER( 'T', [Meas] > 10 )`** | *Same* (This is a core No-Calc function) |
| **`ALLEXCEPT( 'T', 'T'[C] )`** | `FILTER( ALL('T'), 'T'[C] IN VALUES('T'[C]) )` |
| **`ALLSELECTED( 'T' )`** | `VAR __Context = VALUES('T') ... FILTER( ALL('T'), 'T' IN __Context )` |

### Relationship Handling

| Standard Function | No-CALCULATE Equivalent Pattern |
| :--- | :--- |
| **`USERELATIONSHIP( 'T'[Ship], 'D'[Date] )`** | `VAR __Dates = VALUES('D'[Date]) RETURN FILTER( 'T', 'T'[Ship] IN __Dates )` |
| **`CROSSFILTER( ... )`** | *Manual implementation*: Filter one table based on values of another using `INTERSECT` or `IN`. |
| **`RELATED( 'T'[Col] )`** | *Same* (Core function). |
| **`RELATEDTABLE( 'T' )`** | `FILTER( 'T', 'T'[Key] = EARLIER('Parent'[Key]) )` or simply rely on filter propagation. |

### Context Modification

| Standard Function | No-CALCULATE Equivalent Pattern |
| :--- | :--- |
| **`KEEPFILTERS( ... )`** | `VAR __Current = VALUES('T'[C]) RETURN FILTER( 'T', 'T'[C] = "X" && 'T'[C] IN __Current )` |
| **`REMOVEFILTERS( 'T'[C] )`** | `ALL( 'T'[C] )` |
| **`EARLIER()`** | Use Variables `VAR __CurrentRowVal = [Col]` instead. |

