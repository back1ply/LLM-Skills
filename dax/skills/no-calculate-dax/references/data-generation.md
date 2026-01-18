# Data Generation Patterns

Patterns for creating test data, sequences, and lookup tables in DAX.

---

## GENERATESERIES - Number Sequences

Create a sequence of numbers:

```dax
Numbers 1 to 100 = GENERATESERIES( 1, 100, 1 )
```

With custom step:
```dax
Percentages = GENERATESERIES( 0, 1, 0.05 )  // 0, 0.05, 0.10, ... 1.00
```

---

## Calendar Table (Complete)

Full calendar with all offset columns for time intelligence:

```dax
Calendar = 
    VAR __Today = TODAY()
    VAR __StartDate = DATE( 2020, 1, 1 )
    VAR __EndDate = DATE( 2030, 12, 31 )
    VAR __CurrYear = YEAR( __Today )
    VAR __CurrQuarter = QUARTER( __Today )
    VAR __CurrMonth = __CurrYear * 12 + MONTH( __Today )
    VAR __CurrWeek = __CurrYear * 52 + WEEKNUM( __Today, 2 )
    
    VAR __Base = CALENDAR( __StartDate, __EndDate )
    
    VAR __Table = ADDCOLUMNS(
        __Base,
        "Year", YEAR( [Date] ),
        "Quarter", "Q" & FORMAT( [Date], "Q" ),
        "QuarterNum", QUARTER( [Date] ),
        "Month", FORMAT( [Date], "mmmm" ),
        "MonthNum", MONTH( [Date] ),
        "MonthShort", FORMAT( [Date], "mmm" ),
        "Day", DAY( [Date] ),
        "Weekday", FORMAT( [Date], "dddd" ),
        "WeekdayNum", WEEKDAY( [Date], 2 ),
        "WeekNum", WEEKNUM( [Date], 2 ),
        "YearMonth", FORMAT( [Date], "yyyy-mm" ),
        "YearQuarter", YEAR( [Date] ) & "-Q" & FORMAT( [Date], "Q" ),
        
        // Offset columns (0 = current period)
        "CurrYearOffset", YEAR( [Date] ) - __CurrYear,
        "CurrQuarterOffset", 
            ( YEAR( [Date] ) * 4 + QUARTER( [Date] ) ) - 
            ( __CurrYear * 4 + __CurrQuarter ),
        "CurrMonthOffset", 
            ( YEAR( [Date] ) * 12 + MONTH( [Date] ) ) - __CurrMonth,
        "CurrWeekOffset", 
            ( YEAR( [Date] ) * 52 + WEEKNUM( [Date], 2 ) ) - __CurrWeek,
        
        // Flags
        "IsCurrentYear", IF( YEAR( [Date] ) = __CurrYear, TRUE, FALSE ),
        "IsCurrentMonth", 
            IF( YEAR( [Date] ) = __CurrYear && MONTH( [Date] ) = MONTH( __Today ), TRUE, FALSE ),
        "IsFuture", IF( [Date] > __Today, TRUE, FALSE ),
        "IsWeekend", IF( WEEKDAY( [Date], 2 ) > 5, TRUE, FALSE )
    )
    
    RETURN __Table
```

> **Important**: Set Sort by Column for `Month` to `MonthNum`, `Weekday` to `WeekdayNum`, `Quarter` to `QuarterNum`.

---

## Time Table

Generate time slots for time-based analysis:

### Every Hour
```dax
Hours Table = 
    ADDCOLUMNS(
        GENERATESERIES( 0, 23, 1 ),
        "Time", TIME( [Value], 0, 0 ),
        "Hour", [Value],
        "TimeLabel", FORMAT( TIME( [Value], 0, 0 ), "hh:mm AM/PM" ),
        "Period", SWITCH(
            TRUE(),
            [Value] < 6, "Night",
            [Value] < 12, "Morning",
            [Value] < 18, "Afternoon",
            "Evening"
        )
    )
```

### Every 15 Minutes
```dax
Time Slots = 
    VAR __MinutesInDay = 24 * 60
    VAR __Interval = 15
    VAR __Slots = GENERATESERIES( 0, __MinutesInDay - __Interval, __Interval )
    
    RETURN ADDCOLUMNS(
        __Slots,
        "Time", TIME( TRUNC( [Value] / 60 ), MOD( [Value], 60 ), 0 ),
        "Hour", TRUNC( [Value] / 60 ),
        "Minute", MOD( [Value], 60 ),
        "TimeLabel", FORMAT( TIME( TRUNC( [Value] / 60 ), MOD( [Value], 60 ), 0 ), "hh:mm" )
    )
```

---

## Mock Data with RANDBETWEEN

Generate random test data:

```dax
Test Sales = 
    VAR __Dates = CALENDAR( DATE( 2024, 1, 1 ), DATE( 2024, 12, 31 ) )
    VAR __Products = { "Widget", "Gadget", "Gizmo", "Thingamajig" }
    VAR __Regions = { "North", "South", "East", "West" }
    
    VAR __Base = CROSSJOIN( __Dates, __Products, __Regions )
    
    RETURN ADDCOLUMNS(
        __Base,
        "Quantity", RANDBETWEEN( 1, 100 ),
        "UnitPrice", RANDBETWEEN( 10, 500 ) / 10,
        "Discount", RANDBETWEEN( 0, 20 ) / 100
    )
```

> **Note**: RANDBETWEEN recalculates on every refresh. For stable test data, use Power Query instead.

---

## Measure Tables

Create dedicated tables to organize measures in the model. This keeps the Fields pane clean and groups related measures together.

> **Full Guide**: See [Measure Organization & Best Practices](./measure-organization.md#measure-tables-display-tables) for detailed instructions on creating measure tables and display folders.

---

## Parameter Tables (Disconnected)

For creating "Dynamic Measure Selectors" or "Top N Selectors", you can generate static tables using DAX or Power Query.

> **Full Patterns**: See [Measure Organization](./measure-organization.md#parameter-measure-pattern) for the Measure Selector pattern, and [Advanced & Complex Patterns](./advanced-complex-patterns.md#disconnected-tables) for "Not Slicers" and "And Slicers".

### Numeric Range Selector
```dax
Top N Selector = 
    UNION(
        ROW( "Value", 5, "Label", "Top 5" ),
        ROW( "Value", 10, "Label", "Top 10" ),
        ROW( "Value", 20, "Label", "Top 20" ),
        ROW( "Value", 50, "Label", "Top 50" )
    )
```

---

## Fiscal Calendar

Fiscal year starting in July:

```dax
Fiscal Calendar = 
    VAR __FiscalYearStartMonth = 7
    VAR __Base = CALENDAR( DATE( 2020, 1, 1 ), DATE( 2030, 12, 31 ) )
    
    RETURN ADDCOLUMNS(
        __Base,
        "FiscalYear", 
            IF( MONTH( [Date] ) >= __FiscalYearStartMonth, 
                YEAR( [Date] ) + 1, 
                YEAR( [Date] ) ),
        "FiscalQuarter", 
            "FQ" & ( CEILING( ( MONTH( [Date] ) - __FiscalYearStartMonth + 12 ) / 3, 1 ) - 3 ),
        "FiscalMonth", 
            MOD( MONTH( [Date] ) - __FiscalYearStartMonth + 12, 12 ) + 1,
        "FiscalPeriod", 
            "FY" & IF( MONTH( [Date] ) >= __FiscalYearStartMonth, 
                YEAR( [Date] ) + 1, 
                YEAR( [Date] ) ) & "-P" & 
            FORMAT( MOD( MONTH( [Date] ) - __FiscalYearStartMonth + 12, 12 ) + 1, "00" )
    )
```

---

## Population Table (for Lorenz/Gini)

Generate percentage points for cumulative distribution charts:

```dax
Population Percentiles = 
    ADDCOLUMNS(
        GENERATESERIES( 0, 1, 0.01 ),
        "Percentile", [Value] * 100,
        "Label", FORMAT( [Value], "0%" )
    )
```

---

## Power Query Calendar (Recommended)

For production, use Power Query instead of DAX to create calendar tables. DAX calendar tables recalculate on every refresh, while Power Query calendars are pre-computed and more performant.

### Melissa de Korte's Extended Date Table

The best Power Query calendar function is Melissa de Korte's Extended Date Table:

**Source**: [Enterprise DNA Forum - Extended Date Table](https://forum.enterprisedna.co/t/extended-date-table-power-query-m-function/6390)

This M function includes 60+ columns:
- Standard offsets (Year, Quarter, Month, Week, Day)
- Fiscal year offsets with configurable start month
- ISO week columns (ISO Year, ISO Week)
- Flags (IsCurrentYear, IsCurrentMonth, IsWeekend, IsFuture)

### Setup Steps

1. **Get the code**: Copy the `fnDateTable` function from the Enterprise DNA link
2. **Create Blank Query**: Get Data → Blank Query → Advanced Editor
3. **Paste the code**: Replace all content with the function code
4. **Rename**: Call it `fxCalendar`
5. **Invoke the function** with parameters:
   - `StartDate`: e.g., `1/1/2020`
   - `EndDate`: e.g., `12/31/2030`
   - `FYStartMonthNum`: Fiscal year start (e.g., `7` for July)
6. **Rename result**: Call it `Calendar`
7. **Close & Apply**

### Configure Sort by Column

After loading, set these sort relationships in Power BI:
- `Month Name` → Sort by `Month` (month number)
- `Weekday` → Sort by `WeekdayNum`
- `Quarter` → Sort by `QuarterNum`

> **Tip**: Right-click a column → Sort by Column → Select the sort column

### Mark as Date Table

For DAX time intelligence functions (if used):
1. Right-click the Calendar table in the Data pane
2. Select "Mark as date table"
3. Choose the Date column

> **Note**: The No CALCULATE approach uses offsets instead of time intelligence functions, so marking isn't required.

---

## Quick Reference

| Pattern | Function | Use Case |
|---------|----------|----------|
| `GENERATESERIES(start, end, step)` | Number sequence | Loops, percentiles |
| `CALENDAR(start, end)` | Date sequence | Date tables |
| `CROSSJOIN(t1, t2)` | All combinations | Test data, matrices |
| `RANDBETWEEN(min, max)` | Random integer | Mock data |
| `UNION(ROW(...), ROW(...))` | Manual table | Parameter tables |
| `{ "A", "B", "C" }` | Table constructor | Simple lists |
