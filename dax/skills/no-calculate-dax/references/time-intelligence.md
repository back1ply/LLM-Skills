# Time Intelligence Patterns

> **This is the primary reference** for time intelligence patterns using the No CALCULATE methodology. For context-aware variants (Card vs Table behavior), see [Visual Context: Card vs Table Trap](./visual-context.md#visual-consistency-the-card-vs-table-trap). For refactoring examples, see [Refactoring Examples](./refactoring-examples.md#3-time-intelligence-ytd).

No CALCULATE approach to time intelligence using offsets instead of built-in functions like `TOTALYTD`.

> [!IMPORTANT]
> Standard time intelligence functions (`TOTALYTD`, `SAMEPERIODLASTYEAR`, etc.) behave **inconsistently** across visual types. The offset pattern works **consistently everywhere** because the logic is explicit. 
> 
> For a detailed comparison of visual behavior (Card vs Table) and the "Why it works" analysis, see [Visual Context: Card vs Table Trap](./visual-context.md#visual-consistency-the-card-vs-table-trap).

## Offset Convention

Calendar table should have offset columns where:

- `0` = current period
- `-1` = previous period
- `1` = next period

| Column Name | Description |
|-------------|-------------|
| `CurrYearOffset` | Years from current year |
| `CurrQuarterOffset` | Quarters from current quarter |
| `CurrMonthOffset` | Months from current month |
| `CurrWeekOffset` | Weeks from current week |

---

## Calendar Table with Offsets

A Calendar table with offset columns is fundamental to No CALCULATE time intelligence. For complete Calendar table implementation including:
- Full DAX Calendar with all offset columns
- Power Query Calendar (recommended for production)
- Fiscal year support

See [Data Generation: Calendar Table](./data-generation.md#calendar-table-complete).

### Quick Offset Summary

| Column | Description |
|--------|-------------|
| `CurrYearOffset` | 0 = current year, -1 = last year, 1 = next year |
| `CurrMonthOffset` | 0 = current month, -1 = last month |
| `CurrQuarterOffset` | 0 = current quarter |
| `CurrWeekOffset` | 0 = current week |

**Quick Example (Calculated Column in Calendar table)**:
```dax
CurrYearOffset = YEAR( [Date] ) - YEAR( TODAY() )
CurrMonthOffset = ( YEAR( [Date] ) - YEAR( TODAY() ) ) * 12 + ( MONTH( [Date] ) - MONTH( TODAY() ) )
```

> **For complete implementation**, see [Data Generation: Calendar Table](./data-generation.md#calendar-table-complete) for full DAX calendar with all offset columns, Power Query version, and fiscal year support.

---

## Period-to-Date (Generic Template)

Use this template for YTD, QTD, MTD, or WTD — just swap `[OffsetColumn]`:

| Period | OffsetColumn | HASONEVALUE Check |
|--------|--------------|-------------------|
| Year | `CurrYearOffset` | `[Year]` |
| Quarter | `CurrQuarterOffset` | `[Year], [Quarter]` |
| Month | `CurrMonthOffset` | `[Year], [Month]` |
| Week | `CurrWeekOffset` | `[Year], [WeekNum]` |

```dax
Month To Date = 
    VAR __Offset = IF( 
        HASONEVALUE( 'Calendar'[Year] ) && HASONEVALUE( 'Calendar'[Month] ),
        MAX( 'Calendar'[CurrMonthOffset] ), 
        0 
    )
    VAR __MaxDate = IF( __Offset = 0, TODAY(), MAX( 'Calendar'[Date] ) )
    VAR __Table = SUMMARIZE(
        FILTER( 'Calendar', [Date] <= __MaxDate && [CurrMonthOffset] = __Offset ),
        [Date], "__Value", SUM( 'Sales'[Amount] )
    )
    RETURN SUMX( __Table, [__Value] )
```

### The Logic Behind the Pattern (Why this works)

This pattern didn't appear out of thin air. It evolved to solve specific problems with simpler approaches.

**Attempt 1 (The Basic Filter)**:
`FILTER( 'Calendar', [Date] <= TODAY() )`
*   **Problem**: Shows data up to today for *every* year. You can't compare "Jan-Feb 2023" vs "Jan-Feb 2024" because 2023 shows full year.

**Attempt 2 (The Max Date)**:
`FILTER( 'Calendar', [Date] <= MAX('Calendar'[Date]) )`
*   **Problem**: In a Card visual, `MAX('Date')` is the end of time (2030+), showing future budget/forecast data instead of actuals.

**The Solution (Offset Logic)**:
We need a hybrid rule:
1.  **If Current Year**: Stop at `TODAY()`.
2.  **If Past Year**: Stop at the *equivalent* max date (end of year).
3.  **If Future Year**: Show nothing (or up to max).

This is why we calculate `__MaxDate` dynamically:
```dax
VAR __MaxDate = IF( __Offset = 0, TODAY(), MAX( 'Calendar'[Date] ) )
```


### Simple Example (YTD)

```dax
Sales YTD = 
    VAR __Today = TODAY()
    VAR __Table = SUMMARIZE(
        FILTER( 'Calendar', [Date] <= __Today && [CurrYearOffset] = 0 ),
        [Date], "__Value", SUM( 'Sales'[Amount] ) 
    )
    RETURN SUMX( __Table, [__Value] )
```

### Week-to-Date (WTD)

```dax
Sales WTD = 
    VAR __Offset = IF( 
        HASONEVALUE( 'Calendar'[Year] ) && HASONEVALUE( 'Calendar'[WeekNum] ),
        MAX( 'Calendar'[CurrWeekOffset] ), 
        0 
    )
    VAR __Today = TODAY()
    VAR __MaxDate = IF( __Offset = 0, __Today, MAX( 'Calendar'[Date] ) )
    VAR __Table = SUMMARIZE(
        FILTER( 'Calendar', [Date] <= __MaxDate && [CurrWeekOffset] = __Offset ),
        [Date], "__Value", SUM( 'Sales'[Amount] )
    )
    RETURN SUMX( __Table, [__Value] )
```

> [!NOTE]
> Week-to-Date is particularly useful for retail/operations dashboards where weekly cycles matter more than monthly.

---

## Previous Period (Generic Template)

Use this for Previous Year, Quarter, Month, or Week:

```dax
Previous [Period] = 
    VAR __Offset = MAX( 'Calendar'[OffsetColumn] ) - 1
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), [OffsetColumn] = __Offset ),
        [Date], "__Value", SUM( 'Sales'[Amount] )
    )
    RETURN SUMX( __Table, [__Value] )
```

### Simple Example (Previous Year)

```dax
Sales Previous Year = 
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), [CurrYearOffset] = -1 ),
        [Date], "__Value", SUM( 'Sales'[Amount] ) 
    )
    RETURN SUMX( __Table, [__Value] )
```

---

## Previous Period-to-Date (PYTD)

Compare current YTD to same point last year:

```dax
Sales PYTD = 
    VAR __Today = TODAY()
    VAR __SameDayLastYear = DATE( YEAR( __Today ) - 1, MONTH( __Today ), DAY( __Today ) )
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), [Date] <= __SameDayLastYear && [CurrYearOffset] = -1 ),
        [Date], "__Value", SUM( 'Sales'[Amount] ) 
    )
    RETURN SUMX( __Table, [__Value] )
```

---

## Rolling N-Period Average

```dax
Rolling 6 Month Average = 
    VAR __N = 6
    VAR __MaxOffset = MAX( 'Calendar'[CurrMonthOffset] ) - 1
    VAR __MinOffset = __MaxOffset - __N + 1
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), [CurrMonthOffset] >= __MinOffset && [CurrMonthOffset] <= __MaxOffset ),
        [Month], "__Value", SUM( 'Sales'[Amount] )
    )
    RETURN AVERAGEX( __Table, [__Value] )  -- Use SUMX for rolling sum
```

---

## Running Total

```dax
Cumulative Sales =
    VAR __Date = MAX( 'Calendar'[Date] )
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), [Date] <= __Date ),
        [Date], "__Value", SUM( 'Sales'[Amount] ) )
    RETURN SUMX( __Table, [__Value] )
```

---

## Previous Row Value

```dax
Previous Value =
    VAR __Current = MAX( 'Table'[Date] )
    VAR __Previous = MAXX( FILTER( ALL( 'Table' ), [Date] < __Current ), [Date] )
    RETURN SUMX( FILTER( ALL( 'Table' ), [Date] = __Previous ), [Value] )
```

### Previous Occurrence (Any Column)

Find the previous occurrence based on any ordered column (ID, sequence number, etc.):

```dax
Previous by ID = 
    VAR __CurrentID = MAX( 'Table'[ID] )
    VAR __PreviousID = MAXX( FILTER( ALL( 'Table' ), [ID] < __CurrentID ), [ID] )
    VAR __Result = MAXX( FILTER( ALL( 'Table' ), [ID] = __PreviousID ), [Value] )
    RETURN __Result
```

### Next Row Value

```dax
Next Value = 
    VAR __Current = MAX( 'Table'[Date] )
    VAR __Next = MINX( FILTER( ALL( 'Table' ), [Date] > __Current ), [Date] )
    RETURN SUMX( FILTER( ALL( 'Table' ), [Date] = __Next ), [Value] )
```

### Change from Previous

```dax
Change from Previous = 
    VAR __Current = [Current Value]
    VAR __Previous = [Previous Value]
    VAR __Result = __Current - __Previous
    RETURN __Result

Change % from Previous = 
    VAR __Current = [Current Value]
    VAR __Previous = [Previous Value]
    VAR __Result = DIVIDE( __Current - __Previous, __Previous, 0 )
    RETURN __Result
```

---

## Leap Year Detection

Check if a year is a leap year:

```dax
IsLeapYear = 
    VAR __Year = MAX( 'Calendar'[Year] )
    VAR __Div4 = MOD( __Year, 4 ) = 0
    VAR __Div100 = MOD( __Year, 100 ) = 0
    VAR __Div400 = MOD( __Year, 400 ) = 0
    VAR __Result = SWITCH(
        TRUE(),
        __Div4 && NOT( __Div100 ), TRUE(),
        __Div4 && __Div100 && __Div400, TRUE(),
        FALSE()
    )
    RETURN __Result
```

---

## Julian Day Conversion

Convert Gregorian date to Julian Day (for astronomical/scientific use):

```dax
Julian Day = 
    VAR __Date = MAX( 'Calendar'[Date] )
    VAR __Year = YEAR( __Date )
    VAR __Month = MONTH( __Date )
    VAR __Day = DAY( __Date )
    VAR __Y = IF( __Month > 2, __Year, __Year - 1 )
    VAR __M = IF( __Month > 2, __Month, __Month + 12 )
    VAR __A = INT( __Y / 100 )
    VAR __B = 2 - __A + INT( __A / 4 )
    VAR __Result = INT( 365.25 * ( __Y + 4716 ) ) + 
                   INT( 30.6001 * ( __M + 1 ) ) + 
                   __Day + __B - 1524.5
    RETURN __Result
```

---

## Rolling Period Sum (alternative)

Sum instead of average over rolling period:

```dax
Rolling 12 Month Sum = 
    VAR __MaxOffset = MAX( 'Calendar'[CurrMonthOffset] )
    VAR __MinOffset = __MaxOffset - 11
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), 
                [CurrMonthOffset] >= __MinOffset && [CurrMonthOffset] <= __MaxOffset ),
        [Month], "__Value", SUM( 'Sales'[Amount] )
    )
    RETURN SUMX( __Table, [__Value] )
```

---

## Rolling Period-to-Date Average

Average of same-point-in-time across multiple years (handles leap years):

```dax
Rolling 3 YTD Average = 
    VAR __MaxOffset = MAX( 'Calendar'[CurrYearOffset] ) - 1
    VAR __MinOffset = __MaxOffset - 2
    VAR __Today = TODAY()
    VAR __DayOfYear = __Today - DATE( YEAR( __Today ), 1, 1 )
    VAR __Table = SUMMARIZE(
        FILTER( ALL( 'Calendar' ), 
                [CurrYearOffset] >= __MinOffset && 
                [CurrYearOffset] <= __MaxOffset &&
                [Date] - DATE( YEAR( [Date] ), 1, 1 ) <= __DayOfYear
        ),
        [Year], "__Value", SUM( 'Sales'[Amount] )
    )
    RETURN AVERAGEX( __Table, [__Value] )
```

---

## Dynamic Offsets (Single-Table Models)

You don't need a separate calendar table with pre-computed offsets. Create offsets dynamically within the measure itself:

### Month-to-Date (Single Table)

For models with only a fact table containing a Date column:

```dax
MTD Single Table = 
    VAR __Offset = IF( 
        HASONEVALUE( 'Sales'[Year] ) && HASONEVALUE( 'Sales'[Month] ),
        YEAR( MAX( 'Sales'[Date] ) ) * 100 + MONTH( MAX( 'Sales'[Date] ) ), 
        YEAR( TODAY() ) * 100 + MONTH( TODAY() ) 
    )
    VAR __Table = SUMMARIZE( 
        ADDCOLUMNS( 'Sales', "__Offset", YEAR( [Date] ) * 100 + MONTH( [Date] ) ),
        [__Offset], "__Value", SUM( 'Sales'[Amount] ) 
    )
    VAR __Result = SUMX( FILTER( __Table, [__Offset] <= __Offset ), [__Value] )
    RETURN __Result
```

### Dynamic Year Offset (Calculated Column Alternative)

Create the offset dynamically instead of storing it:

```dax
Year Offset Dynamic = 
    VAR __CurrentYear = YEAR( TODAY() )
    VAR __RowYear = YEAR( MAX( 'Sales'[Date] ) )
    RETURN __RowYear - __CurrentYear
```

### Dynamic Month Offset

```dax
Month Offset Dynamic = 
    VAR __Today = TODAY()
    VAR __Current = YEAR( __Today ) * 12 + MONTH( __Today )
    VAR __Row = YEAR( MAX( 'Sales'[Date] ) ) * 12 + MONTH( MAX( 'Sales'[Date] ) )
    RETURN __Row - __Current
```

> **Use case**: Single-table models, quick prototypes, or when you can't modify the calendar table.

> [!IMPORTANT]
> Pre-computed offset columns in a calendar table are more performant for large datasets. Use dynamic offsets for small models or when flexibility is needed.

---

## Related References

- [Data Generation](./data-generation.md) — Creating calendar tables with offset columns
- [Time & Duration Patterns](./time-duration-patterns.md) — Time zones, Unix timestamps, NETWORKDAYS

