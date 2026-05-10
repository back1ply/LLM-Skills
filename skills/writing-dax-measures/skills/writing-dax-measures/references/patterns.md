# Advanced DAX Patterns

Reference file for relationships, running totals, rankings, and other advanced calculations.

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
