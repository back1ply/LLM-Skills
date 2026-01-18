# Automated Testing Patterns

Using DAX Query View to create unit tests for your No-CALCULATE measures.

## Why Test?

Logic without `CALCULATE` is more predictable, but complex business rules (like tiered commissions or specific fiscal calendars) still require verification. Automated tests ensure that future changes don't break existing logic.

## The Testing Pattern

Use `DEFINE`, `EVALUATE`, and error-raising patterns to create a "Test Runner".

> **See also**: [DAX Query View Patterns](./dax-query-patterns.md) for the foundational query structure used in these tests.

### Basic Test Structure

```dax
DEFINE
    -- 1. Mock Data / Define Measure locally (Optional, for isolation)
    MEASURE Sales[TestMeasure] = SUM( Sales[Amount] )
    
    -- 2. Define Test Logic
    VAR __Expected = 100
    VAR __Actual = [TestMeasure]
    VAR __TestPassed = __Actual = __Expected

EVALUATE
    -- 3. Output Result
    {
        ( "Test Name", IF( __TestPassed, "PASS", "FAIL" ), __Expected, __Actual )
    }
```

---

## DAX Unit Testing Framework

You can create a robust test suite using a single DAX query.

### The "ASSERT" Pattern

Since DAX doesn't have a native `ASSERT` function that stops execution, we use a simple table construction to list results.

```dax
DEFINE
    -- Reference your actual measures here
    MEASURE 'Sales'[Local_YTD] = 
        VAR __Date = DATE(2024, 1, 31)
        VAR __Offset = 0 -- Assuming 0 is Current Year
        RETURN CALCULATE( [Sales YTD], 'Calendar'[Date] = __Date ) 
        -- Note: We use CALCULATE here only to set the *Test Context*, not inside the measure logic itself!

EVALUATE
    UNION(
        -- Test 1: Verify YTD Accumulation
        ROW(
            "Test", "YTD Accumulation",
            "Result", IF( [Local_YTD] > 0, "PASS", "FAIL" ),
            "Details", "Value: " & [Local_YTD]
        ),
        
        -- Test 2: Verify Fiscal Reset
        ROW(
            "Test", "Fiscal Reset",
            "Result", IF( [Sales YTD] = [Sales MTD], "PASS", "FAIL" ), -- Should match in Month 1
            "Details", "Diff: " & ([Sales YTD] - [Sales MTD])
        )
    )
```

---

## Testing "No CALCULATE" Specifics

Because No-CALCULATE measures rely on `ALL` and explicit filtering, it is critical to test them in **Filtered Contexts** to ensure they respect (or ignore) slicers correctly.

### Testing Context Interactions

```dax
DEFINE 
    MEASURE 'Tests'[Test_Filter_Respect] = 
        VAR __Color = "Red"
        -- Simulate a slicer selection using TREATAS or explicitly setting context
        VAR __Result = 
            CALCULATE(
                [Total Sales],
                'Product'[Color] = __Color
            )
        RETURN __Result

EVALUATE
    {
        ( "Respects Color Filter", [Test_Filter_Respect] )
    }
```

---

## Mocking Data

For pure logic testing, generate mock data on the fly so your tests don't depend on the actual database state.

```dax
EVALUATE
    VAR __MockTable = 
        DATATABLE(
            "Category", STRING, "Amount", INTEGER,
            {
                { "A", 10 },
                { "B", 20 },
                { "A", 30 }
            }
        )
    VAR __TestResult = SUMX( FILTER( __MockTable, [Category] = "A" ), [Amount] )
    RETURN
        { ( "Filter Logic Check", IF( __TestResult = 40, "PASS", "FAIL" ) ) }
```

---

## Pipeline Integration

You can run these DAX queries using the **Fabric REST API** or **ExecuteQuery** in PowerShell/Python to fail your build pipeline if a DAX test returns "FAIL".
