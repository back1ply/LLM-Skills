# Power Query (M) Patterns

The "No CALCULATE" methodology often relies on specific table structures that are best created in Power Query (M) rather than DAX.

## Extended Date Table

A robust calendar table with pre-computed offsets is essential for simple time intelligence measures.

```powerquery
let
    // Configuration
    StartDate = #date(2020, 1, 1),
    EndDate = #date(2030, 12, 31),
    FiscalYearStartMonth = 7,

    // Generation
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    Source = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    TableFromList = Table.FromList(Source, Splitter.SplitByNothing(), {"Date"}),
    ChangedType = Table.TransformColumnTypes(TableFromList,{{"Date", type date}}),

    // Standard Columns
    InsertYear = Table.AddColumn(ChangedType, "Year", each Date.Year([Date]), Int64.Type),
    InsertQuarter = Table.AddColumn(InsertYear, "Quarter", each "Q" & Number.ToText(Date.QuarterOfYear([Date])), type text),
    InsertMonth = Table.AddColumn(InsertQuarter, "Month", each Date.MonthName([Date]), type text),
    InsertMonthNum = Table.AddColumn(InsertMonth, "MonthNum", each Date.Month([Date]), Int64.Type),
    InsertWeek = Table.AddColumn(InsertMonthNum, "WeekNum", each Date.WeekOfYear([Date]), Int64.Type),
    InsertDay = Table.AddColumn(InsertWeek, "Day", each Date.Day([Date]), Int64.Type),
    InsertDayName = Table.AddColumn(InsertDay, "DayName", each Date.DayOfWeekName([Date]), type text),
    
    // Sort Columns
    InsertMonthYear = Table.AddColumn(InsertDayName, "MonthYearSort", each [Year] * 100 + [MonthNum], Int64.Type),
    InsertQtrYear = Table.AddColumn(InsertMonthYear, "QuarterYearSort", each [Year] * 100 + Date.QuarterOfYear([Date]), Int64.Type),

    // Offsets (Crucial for Time Intelligence)
    CurrentDate = Date.From(DateTime.LocalNow()),
    CurrentYear = Date.Year(CurrentDate),
    CurrentMonth = Date.Month(CurrentDate),
    CurrentQuarter = Date.QuarterOfYear(CurrentDate),
    
    // Year Offset: 0 = Current Year, -1 = Last Year
    InsertYearOffset = Table.AddColumn(InsertQtrYear, "CurrYearOffset", each [Year] - CurrentYear, Int64.Type),
    
    // Month Offset: 0 = Current Month, -1 = Last Month
    InsertMonthOffset = Table.AddColumn(InsertYearOffset, "CurrMonthOffset", each 
        ((12 * [Year]) + [MonthNum]) - ((12 * CurrentYear) + CurrentMonth), Int64.Type),

    // Quarter Offset
    InsertQuarterOffset = Table.AddColumn(InsertMonthOffset, "CurrQuarterOffset", each 
        ((4 * [Year]) + Date.QuarterOfYear([Date])) - ((4 * CurrentYear) + CurrentQuarter), Int64.Type)

in
    InsertQuarterOffset
```

## Disconnected Parameter Tables

For "AND Slicers", "Measure Selectors", or "Custom Hierarchies", create static tables in Power Query using `Table.FromRows`.

### Measure Selector Table

```powerquery
let
    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WcixALOBUiFKK1YlWcivKK8xC8ZzMQrCQW2JRSQZE2C8xN1UpNhYA", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [MeasureName = _t, Type = _t]),
    ChangedType = Table.TransformColumnTypes(Source,{{"MeasureName", type text}, {"Type", type text}})
in
    ChangedType
```

**Generates:**
| MeasureName | Type |
|-------------|------|
| Sales | Currency |
| Quantity | Integer |
| Margin % | Percent |

### Custom Hierarchy Table

For the Matrix visual override pattern.

```powerquery
let
    // Create base years
    Years = {2020..2025},
    
    // Generate Months for each year
    ExpandMonths = List.TransformMany(Years, each {1..12}, (y, m) => 
        [Value1 = Text.From(y), Value2 = Date.MonthName(#date(y, m, 1)), Value3 = m, Type = "Detail"]),
    
    // Create specific Totals
    Totals = {
        [Value1 = "Total", Value2 = "CY", Value3 = 100, Type = "Total"],
        [Value1 = "Total", Value2 = "LY", Value3 = 101, Type = "Total"],
        [Value1 = "Total", Value2 = "Diff", Value3 = 102, Type = "Total"]
    },
    
    Combine = ExpandMonths & Totals,
    ToTable = Table.FromList(Combine, Record.FieldValues, {"Value1", "Value2", "Value3", "Type"}),
    TypeCols = Table.TransformColumnTypes(ToTable,{{"Value1", type text}, {"Value2", type text}, {"Value3", Int64.Type}, {"Type", type text}})
in
    TypeCols
```

## Data Cleaning Best Practices

Clean data prevents complex DAX error handling.

### Replace Errors/Nulls

```powerquery
// Replace nulls with 0 for numeric aggregations
ReplacedNulls = Table.ReplaceValue(PreviousStep, null, 0, Replacer.ReplaceValue, {"Amount", "Quantity"}),

// Replace errors with null or default
ReplacedErrors = Table.ReplaceErrorValues(ReplacedNulls, {{"Column1", null}, {"Column2", ""}})
```

### Unpivot for Attribute-Value Pairs

If your data is wide (Jan, Feb, Mar columns), unpivot it to make it improved for DAX.

```powerquery
// Select ID columns -> Right Click -> Unpivot Other Columns
UnpivotedColumns = Table.UnpivotOtherColumns(Source, {"ProductID", "Year"}, "Month", "Amount")
```
