# Debugging Techniques

The No CALCULATE approach enables powerful debugging by inspecting intermediate variables.

## Why No CALCULATE is Debuggable

> For the full explanation of CALCULATE's debugging problems (black box behavior, hidden context transitions), see [Philosophy: Why Avoid CALCULATE](./philosophy.md#why-avoid-calculate).

With the Variable Pattern, you can `RETURN` any intermediate variable to inspect it, unlike CALCULATE where the operation happens in one opaque step.

---

## Step-by-Step Debugging

Change the `RETURN` statement to return intermediate variables:

```dax
Debug Measure = 
    VAR __Table = FILTER( 'Sales', 'Sales'[Amount] > 100 )
    VAR __Result = SUMX( __Table, [Amount] )
    -- RETURN COUNTROWS(__Table)  -- Debug: see row count
    -- RETURN TOCSV(__Table)       -- Debug: see actual rows
    RETURN __Result
```

---

## Debugging Functions

| Function | Purpose | Example Output |
|----------|---------|----------------|
| `COUNTROWS(__Table)` | Check how many rows are in the filtered table | `5` |
| `TOCSV(__Table)` | Return table as CSV text to see actual data | Shows all columns/rows |
| `TOCSV(__Table, 3)` | Limit to first 3 rows | For large tables |
| `CONCATENATEX(__Table, [Column], ", ")` | See distinct values in a column | `"Apple, Banana"` |

---

## TOCSV Function Parameters

```dax
TOCSV( Table, MaxRows, Delimiter, IncludeHeaders )
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `Table` | (required) | A table, table variable, or table expression |
| `MaxRows` | 10 | Maximum number of rows to return |
| `Delimiter` | `","` | Column delimiter (comma, pipe, tab, etc.) |
| `IncludeHeaders` | TRUE | Whether to include column headers as first row |

### Example Usage

```dax
Debug With TOCSV = 
    VAR __Table = FILTER( 'Sales', 'Sales'[Region] = "North" )
    VAR __Debug = TOCSV( __Table, 5, "|", TRUE )
    RETURN __Debug
```

### Alternative Delimiters

```dax
-- Tab-separated (useful for pasting into Excel)
TOCSV( __Table, 10, UNICHAR(9), TRUE )

-- Newline between values (for single-column tables)
TOCSV( __Table, 10, UNICHAR(10), FALSE )

-- Semicolon (for European locales where comma is decimal separator)
TOCSV( __Table, 10, ";", TRUE )
```

### Debugging Tip: Use Table Visual with Consolas Font

**Patron Recommendation** (Henrik Vestergaard):

Instead of a Card visual, use a **Table visual** for TOCSV debugging:
- Table visual left-aligns text (easier to read)
- Use **Consolas** font for monospaced alignment

Setup:
1. Create Table visual with your debug measure
2. Format → Values → Font family → **Consolas**
3. Values → Text size → 10pt (smaller for more data)

---

## Debugging Workflow

1. **Identify the problem**: Measure returns unexpected value
2. **Add intermediate VARs**: Break complex logic into steps
3. **Return COUNTROWS**: Verify expected row count
4. **Return TOCSV**: See actual data in the filtered table
5. **Check each step**: Return each variable to trace the issue
6. **Restore RETURN**: Once fixed, return the final `__Result`

---

## Common Debugging Scenarios

### Unexpected BLANK

```dax
Debug BLANK = 
    VAR __Table = FILTER( 'Sales', 'Sales'[Category] = "Widget" )
    -- If COUNTROWS returns 0, the filter matched no rows
    RETURN COUNTROWS( __Table )
```

### Wrong Aggregation

```dax
Debug Aggregation = 
    VAR __Table = FILTER( 'Sales', 'Sales'[Year] = 2024 )
    VAR __Sum = SUMX( __Table, [Amount] )
    VAR __Count = COUNTROWS( __Table )
    -- Return both to verify: CONCATENATE( __Sum, " / ", __Count )
    RETURN __Sum
```

### Filter Not Working

```dax
Debug Filter = 
    VAR __FilterValue = "Red"
    VAR __Table = FILTER( 'Sales', 'Sales'[Color] = __FilterValue )
    -- Check what values exist: CONCATENATEX( DISTINCT( 'Sales'[Color] ), [Color], ", " )
    RETURN TOCSV( __Table, 3 )
```

---

## AI-Assisted Debugging

When using LLMs (ChatGPT, Claude, etc.) to help debug DAX:

1. **Export the BIM file**: File → Options → "Create a BIM file"
2. **Upload to the AI**: Provide the BIM file with your question
3. **Include the measure**: Paste the problematic DAX code
4. **Describe the issue**: Expected vs. actual results, context

> **Tip**: The BIM file contains your entire model schema, enabling the AI to write accurate, context-aware DAX without you explaining every table/column.

---

## Error Handling

### IFERROR Pattern

Catch errors and return a fallback value:

```dax
Safe Measure = 
    IFERROR( 
        [Potentially Risky Calculation], 
        0  -- Fallback value
    )
```

### ISERROR Pattern

Check if an expression causes an error:

```dax
Has Error = 
    IF( 
        ISERROR( VALUE( [Text Column] ) ), 
        "Invalid Number", 
        "Valid" 
    )
```

### Custom Error Messages

Use ERROR to raise your own errors:

```dax
Validated Measure = 
    VAR __Value = [Input Value]
    VAR __Result = IF( 
        __Value < 0, 
        ERROR( "Value cannot be negative" ),
        SQRT( __Value )
    )
    RETURN __Result
```

> **Note**: Use IFERROR/ISERROR sparingly in production—they can significantly impact performance.

---

## Debugging Context

Use context detection functions to see what filters are active:

```dax
Active Filters = TOCSV( FILTERS( 'Table'[Column] ) )

Is Year Filtered = ISFILTERED( 'Calendar'[Year] )
```

For comprehensive context detection patterns, see [Function Reference](./function-reference.md#quick-reference).

---

## EVALUATEANDLOG (Advanced)

For tracing table expressions with SQL Server Profiler or DAX Studio:

```dax
Traced Measure = EVALUATEANDLOG( [Original Measure] )
```

With custom label:
```dax
Traced With Label = EVALUATEANDLOG( [Measure], "MyMeasureTrace" )
```

### Using EVALUATEANDLOG

1. Connect DAX Studio or SQL Server Profiler to Power BI
2. Start trace capture
3. Interact with visual containing the traced measure
4. View output in Profiler/DAX Studio trace

> **Warning**: Remove EVALUATEANDLOG before publishing to production — it adds overhead.

---

## Circular Dependencies

DAX throws an error when measures or columns reference each other in a loop.

### Detection Pattern

If you get "circular dependency detected":

1. Check if Measure A → Measure B → Measure A
2. Check if Column A → Column B → Column A  
3. Check if relationships form a loop

### Common Causes

```dax
// ✗ BAD: Measure references itself via calculated column
Sales = SUMX( 'Table', [Calculated Column] )

// Where Calculated Column uses:
Calculated Column = [Sales] / COUNTROWS( 'Table' )
```

### Solution

Break the loop by:
- Using a separate intermediate measure
- Moving calculation to Power Query
- Using direct column references instead of measures in calculated columns

---

## BIM File Export (for AI Debugging)

Export your model schema to share with AI assistants (ChatGPT, Claude, etc.):

### Method 1: Power BI Project (.pbip)

1. File → Save As → Select "Power BI Project" (.pbip) folder format
2. Inside folder, find `model.bim` or `.tmd` files
3. Upload these to AI for context-aware DAX help

### Method 2: Tabular Editor Export

1. Install Tabular Editor (External Tool)
2. File → Save As → model.bim
3. This JSON file contains your full schema

### What to Share with AI

The BIM file includes:
- All tables and columns
- All measures with DAX code
- Relationships
- No actual data (safe to share)

### Example Prompt

```
I have attached my model.bim file. Here's my measure that returns unexpected results:

[Sales YTD] = ...

Expected: 1,234,567
Actual: 0

The visual has a slicer on [Year] = 2024.
```

> **Tip**: AI can write accurate DAX when it knows your exact column names and relationships.

---

## DAX Studio Connection

DAX Studio is the essential tool for debugging and performance analysis.

### Connecting

1. Install DAX Studio (free): https://daxstudio.org
2. Open Power BI Desktop with your report
3. Open DAX Studio → Connect → Power BI Desktop

### Useful Queries

**See all measures:**
```dax
SELECT * FROM $SYSTEM.TMSCHEMA_MEASURES
```

**Test a measure in isolation:**
```dax
EVALUATE
ROW( "Result", [Your Measure] )
```

**Test with filter context:**
```dax
EVALUATE
SUMMARIZECOLUMNS(
    'Calendar'[Year],
    "Sales", [Total Sales]
)
```

### Performance Tracing

1. In DAX Studio: Query → Server Timings (ON)
2. Query → Query Plan (ON)
3. Run your query
4. Check "Server Timings" tab for bottlenecks

---

> **See Also**: [Visual Context Patterns](./visual-context.md#auto-exist-behavior) for Auto-Exist behavior and Value Filter Behavior setting.

---

## Fixing Incorrect Totals ("Banana Pickle Math")

When totals in Table/Matrix visuals don't sum correctly.

### The Problem

A measure shows correct values per row but the Total/Subtotal is **wrong**.

#### When It Happens

- Measure includes a constant (e.g., `SUM([Value]) - 2`)
- Measure calculates ratios or percentages
- Measure involves non-additive logic (MIN, MAX, AVERAGE across rows)

#### Why It Breaks

The Total row **recalculates** the measure over ALL data, not by summing the displayed rows.

### The Fix Pattern

Create a summary table at the visual's granularity, then aggregate:

```dax
Measure With Fixed Total = 
    VAR __Table = SUMMARIZE( 
        'Sales', 
        'Sales'[Category],
        "__Value", [Base Measure] 
    )
    VAR __Result = SUMX( __Table, [__Value] )
    RETURN __Result
```

**Key Insight**: Match the `SUMMARIZE` grouping to the visual's row structure.

### Matrix Visual Fix

For a Matrix with Category and Product in the row hierarchy:

```dax
Matrix Fixed Total = 
    VAR __Table = SUMMARIZE( 
        'Sales', 
        'Sales'[Category], 'Sales'[Product],
        "__Value", [Base Measure] 
    )
    VAR __Result = SUMX( __Table, [__Value] )
    RETURN __Result
```

### Example: Margin with Overhead

**Problem Measure** (totals incorrectly):

```dax
Margin With Overhead = SUM( 'Sales'[Margin] ) - 2
```

**Fixed Measure**:

```dax
Margin With Overhead Fixed = 
    VAR __Table = SUMMARIZE( 
        'Sales', 
        'Sales'[Category],
        "__Value", SUM( 'Sales'[Margin] ) - 2
    )
    VAR __Result = SUMX( __Table, [__Value] )
    RETURN __Result
```

### Debugging Totals

Use TOCSV to verify the summarized table:

```dax
Debug Totals = 
    VAR __Table = SUMMARIZE( 
        'Sales', 
        'Sales'[Category],
        "__Value", [Base Measure] 
    )
    RETURN TOCSV( __Table )
```

This shows exactly what rows contribute to the total calculation.

---

## Debugging Tools Summary

| Tool | Use For |
|------|---------|
| TOCSV | See actual table data |
| COUNTROWS | Verify row counts |
| EVALUATEANDLOG | Profiler/DAX Studio tracing |
| DAX Studio | Performance analysis, query testing |
| Performance Analyzer | Visual-level timing in Power BI |
| BIM Export | AI-assisted debugging |

---

## AI Interaction & Prompting

How to get AI assistants (ChatGPT, Claude, Copilot) to write "No CALCULATE" DAX.

### The Problem

Most AIs are trained on the vast amount of existing DAX on the internet, which is 99% `CALCULATE`-based. If you just ask for a measure, you will get `CALCULATE`.

### The "Golden Prompt"

When asking for DAX, always include these constraints:

> "Please write this DAX using the 'No CALCULATE' methodology. 
> 1. Do not use CALCULATE or CALCULATETABLE. 
> 2. Use FILTER and X-aggregators (SUMX, MINX, MAXX) instead. 
> 3. Use variables to make the logic explicit and debuggable. 
> 4. Think in tables, rows, and columns."

### Specific Scenarios

#### General Measure Request

**User**: "I need a measure for Sales Year-to-Date."

**Prompt**:
> "Write a DAX measure for 'Sales YTD'. 
> Constraint: Do not use TOTALYTD or CALCULATE. 
> Use my Calendar table's offsets. 
> Logic: Sum Sales Amount where Date <= Today AND YearOffset = 0."

#### Debugging Request

**User**: "My measure isn't working."

**Prompt**:
> "Here is my measure (below). It returns the wrong total.
> Please refactor it to use the 'No CALCULATE' variable pattern so I can see intermediate table states. 
> Add `RETURN COUNTROWS(__Table)` at the end so I can check the filter size."

#### Optimization Request

**Prompt**:
> "Optimize this measure. 
> Convert any implicit context transitions to explicit FILTER operations. 
> Ensure strict boolean logic is not used in FILTER; use `&&` or nested FILTERs instead."

### Sharing Context (BIM Files)

To get perfect results, the AI needs to know your schema. Export your model as a BIM file and upload it with your question.

> **Full Instructions**: See the [BIM File Export](#bim-file-export-for-ai-debugging) section above for step-by-step export instructions and example prompts.

### Troubleshooting AI Output

If the AI still uses `CALCULATE`:

1.  **Reinforce**: "You used CALCULATE. Stop. Rewrite it using `FILTER` and `SUMX`."
2.  **Provide Example**: Paste a measure from [core-pattern.md](./core-pattern.md) and say "Follow this pattern."
3.  **Explain Why**: "I need to inspect the table variable, so please expose the filtered table as a `VAR`."


