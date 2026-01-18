# Case Studies: The "Why"

Examples of real-world scenarios where "No CALCULATE" saves the day.

## Case Study 1: The Context Transition Trap

**The Problem**: 
A user needed to calculate "Average Sales per Customer", but only for Customers who bought more than $1000.

**The "Standard" Attempt**:
```dax
Avg High Value Cust = 
    AVERAGEX(
        FILTER( Customer, [Total Sales] > 1000 ),
        [Total Sales]
    )
```

**The Bug**: 
The measure `[Total Sales]` contains a `SUM(Sales[Amount])`. When used inside `AVERAGEX` (an iterator), it triggers **Context Transition**.
*   For every single customer row, it transforms the Row Context into a Filter Context.
*   It calculates `[Total Sales]` for that one customer.
*   **Result**: It works... but it is incredibly slow (25 seconds for 100k customers).

**The "No CALCULATE" Fix**:
```dax
Avg High Value Cust = 
    -- 1. Pre-calculate the table with explicit columns
    VAR __Table = 
        FILTER(
            ADDCOLUMNS( 
                Customer, 
                "__Sales", CALCULATE( SUM(Sales[Amount]) ) -- Only use calc logic here one time
            ),
            [__Sales] > 1000
        )
    -- 2. Average the pre-calculated column
    RETURN AVERAGEX( __Table, [__Sales] )
```
*Wait, you used CALCULATE?*
Yes, but only to initially populate the `ADDCOLUMNS` variable. The iteration happens over the *static column* `[__Sales]`. It does not recalculate for every row during the specific Averaging phase. 

**Better "Pure" Fix**:
```dax
Avg High Value Cust = 
    VAR __Table = 
        FILTER(
            GROUPBY( Sales, Customer[ID], "Total", SUMX( CURRENTGROUP(), Sales[Amount] ) ),
            [Total] > 1000
        )
    RETURN AVERAGEX( __Table, [Total] )
```
**Result**: 25 seconds -> 0.4 seconds.

---

## Case Study 2: The Time Intelligence Spaghetti

**The Problem**: 
A finance report needed "Sales YTD", but the fiscal year ends in June, and they wanted to exclude "Inter-company" transactions dynamically.

**The "Standard" Attempt**:
```dax
Sales YTD Custom = 
    CALCULATE(
        [Total Sales],
        DATESYTD( 'Calendar'[Date], "06-30" ),
        'Sales'[Type] <> "Inter-company"
    )
```
**The Bug**: 
`DATESYTD` overwrites the external filter context on the Date table. But the user applied a "Month Year" slicer. The usage of `CALCULATE` here created a conflict where the "Inter-company" filter was sometimes ignored depending on the visual level order.

**The "No CALCULATE" Fix**:
```dax
Sales YTD Custom = 
    VAR __MaxDate = MAX( 'Calendar'[Date] )
    VAR __FiscalYear = MAX( 'Calendar'[FiscalYear] ) -- e.g. "FY2024"
    
    VAR __Table = FILTER(
        'Sales',
        'Sales'[Type] <> "Inter-company" &&
        RELATED('Calendar'[FiscalYear]) = __FiscalYear &&
        'Sales'[Date] <= __MaxDate
    )
    
    RETURN SUMX( __Table, [Amount] )
```
**Result**: 
Logic is strictly linear. 
1. Get the current View Context (Max Date, Fiscal Year).
2. Filter the Sales table explicitly for those conditions.
3. Sum.
Zero implicit overriding. Zero ambiguity.
