# Operations & HR Patterns

Operational metrics and HR calculations using the No CALCULATE approach.

---

## Overall Equipment Effectiveness (OEE)

Manufacturing productivity metric combining availability, performance, and quality:

```dax
OEE = 
    VAR __PlannedTime = SUM( 'Production'[Planned Production Time] )
    VAR __ActualTime = SUM( 'Production'[Actual Run Time] )
    VAR __ExpectedOutput = SUM( 'Production'[Expected Output] )
    VAR __ActualOutput = SUM( 'Production'[Actual Output] )
    VAR __TotalUnits = SUM( 'Production'[Total Units] )
    VAR __GoodUnits = SUM( 'Production'[Good Units] )
    
    VAR __Availability = DIVIDE( __ActualTime, __PlannedTime, 0 )
    VAR __Performance = DIVIDE( __ActualOutput, __ExpectedOutput, 0 )
    VAR __Quality = DIVIDE( __GoodUnits, __TotalUnits, 0 )
    
    VAR __Result = __Availability * __Performance * __Quality
    RETURN __Result
```

Individual components:

```dax
Availability % = 
    VAR __Planned = SUM( 'Production'[Planned Production Time] )
    VAR __Actual = SUM( 'Production'[Actual Run Time] )
    RETURN DIVIDE( __Actual, __Planned, 0 )

Performance % = 
    VAR __Expected = SUM( 'Production'[Expected Output] )
    VAR __Actual = SUM( 'Production'[Actual Output] )
    RETURN DIVIDE( __Actual, __Expected, 0 )

Quality % = 
    VAR __Total = SUM( 'Production'[Total Units] )
    VAR __Good = SUM( 'Production'[Good Units] )
    RETURN DIVIDE( __Good, __Total, 0 )
```

> **World-class OEE** is typically 85%+ (Availability 90% × Performance 95% × Quality 99.9%).

---

## Order Fulfillment Rate

Percentage of orders fulfilled completely from available inventory:

```dax
Order Fulfillment Rate = 
    VAR __TotalOrders = COUNTROWS( 'Orders' )
    VAR __FulfilledOrders = COUNTROWS( 
        FILTER( 'Orders', [Qty Shipped] >= [Qty Ordered] ) 
    )
    RETURN DIVIDE( __FulfilledOrders, __TotalOrders, 0 )
```

With partial fulfillment tracking:

```dax
Fill Rate % = 
    VAR __TotalOrdered = SUM( 'Orders'[Qty Ordered] )
    VAR __TotalShipped = SUM( 'Orders'[Qty Shipped] )
    RETURN DIVIDE( __TotalShipped, __TotalOrdered, 0 )
```

---

## Employee Satisfaction Score

Survey-based satisfaction metric (similar to NPS methodology):

```dax
Employee Satisfaction = 
    VAR __Table = ALL( 'Survey' )
    VAR __Total = COUNTROWS( __Table )
    VAR __Satisfied = COUNTROWS( FILTER( __Table, [Score] >= 4 ) )  -- 4-5 on 5-point scale
    VAR __Neutral = COUNTROWS( FILTER( __Table, [Score] = 3 ) )
    VAR __Dissatisfied = COUNTROWS( FILTER( __Table, [Score] <= 2 ) )
    
    VAR __Result = DIVIDE( __Satisfied - __Dissatisfied, __Total, 0 ) * 100
    RETURN __Result
```

Average satisfaction score:

```dax
Avg Satisfaction = 
    VAR __Table = ALL( 'Survey' )
    VAR __Result = AVERAGEX( __Table, [Score] )
    RETURN __Result
```

---

## Utilization %

Employee or resource utilization rate:

```dax
Utilization % =
    VAR __DailyHours = 8
    VAR __Start = MIN( 'Hours'[Date] )
    VAR __End = MAX( 'Hours'[Date] )
    VAR __TotalHours = NETWORKDAYS( __Start, __End ) * __DailyHours * 
        COUNTROWS( DISTINCT( 'Hours'[EmployeeID] ) )
    VAR __BillableHours = SUMX(
        FILTER( 'Hours', RELATED( 'Tasks'[Category] ) = "Billable" ), [Hours] )
    RETURN DIVIDE( __BillableHours, __TotalHours, 0 )
```

---

## On-Time In-Full (OTIF)

Supply chain delivery metric:

```dax
OTIF % =
    VAR __Total = COUNTROWS( 'Orders' )
    VAR __OnTime = COUNTROWS( FILTER( 'Orders',
        [Actual Delivery] <= [Promised Delivery] && [Qty Delivered] = [Qty Ordered] ) )
    RETURN DIVIDE( __OnTime, __Total, 0 )
```

### On-Time Only

```dax
On Time % =
    VAR __Total = COUNTROWS( 'Orders' )
    VAR __OnTime = COUNTROWS( FILTER( 'Orders', [Actual Delivery] <= [Promised Delivery] ) )
    RETURN DIVIDE( __OnTime, __Total, 0 )
```

### In-Full Only

```dax
In Full % =
    VAR __Total = COUNTROWS( 'Orders' )
    VAR __InFull = COUNTROWS( FILTER( 'Orders', [Qty Delivered] = [Qty Ordered] ) )
    RETURN DIVIDE( __InFull, __Total, 0 )
```

---

## Delivery Date Variance

Analyze difference between expected and actual delivery:

```dax
Delivery Variance Days = 
    VAR __Expected = MAX( 'Orders'[Expected Delivery] )
    VAR __Actual = MAX( 'Orders'[Actual Delivery] )
    VAR __Result = DATEDIFF( __Expected, __Actual, DAY )
    RETURN __Result  // Positive = late, Negative = early
```

Average delivery variance:

```dax
Avg Delivery Variance = 
    VAR __Table = ADDCOLUMNS(
        'Orders',
        "__Variance", DATEDIFF( [Expected Delivery], [Actual Delivery], DAY )
    )
    VAR __Result = AVERAGEX( __Table, [__Variance] )
    RETURN __Result
```

Delivery status categorization:

```dax
Delivery Status = 
    VAR __Expected = MAX( 'Orders'[Expected Delivery] )
    VAR __Actual = MAX( 'Orders'[Actual Delivery] )
    VAR __Variance = DATEDIFF( __Expected, __Actual, DAY )
    VAR __Result = SWITCH(
        TRUE(),
        ISBLANK( __Actual ), "Pending",
        __Variance < 0, "Early",
        __Variance = 0, "On Time",
        __Variance <= 2, "Slightly Late",
        "Late"
    )
    RETURN __Result
```

Late delivery count:

```dax
Late Deliveries = 
    COUNTROWS(
        FILTER( 'Orders', [Actual Delivery] > [Expected Delivery] )
    )
```

---

## Duration Handling

> **Note**: For comprehensive duration formatting patterns (including Decimal Days to String, Hours to HH:MM, and Seconds to Duration), see [Time & Duration Patterns: Formatting Durations](./time-duration-patterns.md#formatting-durations).

---

## Mean Time Between Failure (MTBF)

```dax
MTBF =
    VAR __TotalOperatingTime = SUM( 'Equipment'[OperatingHours] )
    VAR __FailureCount = COUNTROWS( FILTER( 'Events', [Type] = "Failure" ) )
    RETURN DIVIDE( __TotalOperatingTime, __FailureCount, 0 )
```

---

## Order Cycle Time

Average days from order to delivery:

```dax
Avg Cycle Time =
    VAR __Table = ADDCOLUMNS( 'Orders',
        "__Days", DATEDIFF( [OrderDate], [DeliveryDate], DAY ) )
    RETURN AVERAGEX( __Table, [__Days] )
```

---

## Employee Turnover Rate

```dax
Turnover Rate =
    VAR __Separations = COUNTROWS( FILTER( 'Employees', [Status] = "Separated" ) )
    VAR __AvgHeadcount = DIVIDE(
        COUNTROWS( FILTER( 'Employees', [StartDate] <= TODAY() ) ) +
        COUNTROWS( FILTER( 'Employees', [EndDate] >= TODAY() || ISBLANK( [EndDate] ) ) ),
        2 )
    RETURN DIVIDE( __Separations, __AvgHeadcount, 0 )
```

---

## Days of Supply

Inventory coverage metric:

```dax
Days of Supply =
    VAR __CurrentInventory = SUM( 'Inventory'[Quantity] )
    VAR __AvgDailyUsage = AVERAGEX( 
        SUMMARIZE( 'Usage', [Date], "__Daily", SUM( 'Usage'[Quantity] ) ),
        [__Daily] )
    RETURN DIVIDE( __CurrentInventory, __AvgDailyUsage, 0 )
```

---

## Bradford Factor

Absenteeism severity metric that weighs frequent short absences more heavily than infrequent long absences.

**Formula**: Bradford Factor = S² × D (Instances squared × Days absent)

```dax
Bradford Factor = 
    VAR __Start = MIN( 'Dates'[Date] )
    VAR __End = MAX( 'Dates'[Date] )
    VAR __Employees = DISTINCT( 'Employees'[Employee] )
    
    VAR __Absences = ADDCOLUMNS(
        ADDCOLUMNS(
            FILTER( ALL( 'Absences' ),
                [Employee] IN __Employees &&
                [Start Date] <= __End &&
                [End Date] >= __Start
            ),
            "__Min", MAX( __Start, [Start Date] ),
            "__Max", MIN( __End, [End Date] )
        ),
        "__WorkDays", NETWORKDAYS( [__Min], [__Max] )
    )
    
    VAR __AbsentDays = SUMX( __Absences, [__WorkDays] )
    VAR __Instances = COUNTROWS( __Absences )
    VAR __Result = POWER( __Instances, 2 ) * __AbsentDays
    
    RETURN __Result
```

**Thresholds**: Typical ranges are 0-49 (acceptable), 50-124 (warning), 125+ (action required).

---

## Kaplan-Meier Estimator (Survival Analysis)

Measures probability of "survival" over time (e.g., employee retention, equipment uptime).

```dax
KM Survival = 
    VAR __Day = MAX( 'Days'[Day] )
    VAR __Employees = ADDCOLUMNS( 
        'Employees', 
        "__Days", ( [Term Date] - [Hire Date] ) * 1. + 1 
    )
    
    VAR __KMTable = ADDCOLUMNS(
        ADDCOLUMNS(
            GENERATESERIES( 1, __Day ),
            "d(i)", COUNTROWS( FILTER( __Employees, [__Days] = [Value] ) ),
            "n(i)", COUNTROWS( FILTER( __Employees, [__Days] > [Value] ) )
        ),
        "1-d(i)/n(i)", 1 - DIVIDE( [d(i)], [n(i)], 0 )
    )
    
    VAR __Result = PRODUCTX( __KMTable, [1-d(i)/n(i)] )
    RETURN __Result
```

**Use case**: Employee tenure analysis, equipment failure forecasting, subscription retention.

---

## Gini Coefficient (Pay Equality)

Measures inequality in salary/pay distribution. 0 = perfect equality, 1 = perfect inequality.

### Lorenz Curve (for visualization)
```dax
Lorenz Curve = 
    VAR __CurrentPercent = MAX( 'Population'[Value] )
    VAR __AllEmployees = COUNTROWS( DISTINCT( ALL( 'Employees'[Employee] ) ) )
    
    VAR __Table = ADDCOLUMNS( 'Employees',
        "__Percent",
        VAR __Salary = [Annual Salary]
        VAR __Count = COUNTROWS( FILTER( ALL( 'Employees' ), [Annual Salary] <= __Salary ) )
        RETURN DIVIDE( __Count, __AllEmployees )
    )
    
    VAR __AllIncome = SUMX( 'Employees', [Annual Salary] )
    VAR __Employees = SELECTCOLUMNS( 
        FILTER( __Table, [__Percent] <= __CurrentPercent ), 
        "__Employee", [Employee] 
    )
    VAR __Income = SUMX( FILTER( __Table, [Employee] IN __Employees ), [Annual Salary] )
    
    RETURN DIVIDE( __Income, __AllIncome ) + 0
```

### Gini Coefficient (single value)
```dax
Gini Coefficient = 
    VAR __N = COUNTROWS( 'Employees' )
    VAR __TotalSalary = SUM( 'Employees'[Annual Salary] )
    VAR __SumPairDiffs = SUMX( 
        'Employees', 
        SUMX( 'Employees', ABS( [Annual Salary] - EARLIER( [Annual Salary] ) ) ) 
    )
    VAR __Result = DIVIDE( __SumPairDiffs, 2 * __N * __TotalSalary )
    RETURN __Result
```

---

## Human Capital Value Added (HCVA)

Measures average profit contribution per employee.

**Formula**: HCVA = (Revenue - (Total Cost - Employment Costs)) / FTE

```dax
HCVA = 
    VAR __Revenue = 4000000  // Replace with actual revenue measure
    VAR __TotalCost = 3900000  // Replace with actual cost measure
    VAR __LoadedCostFactor = 1.2  // Benefits multiplier
    VAR __Start = DATE( 2024, 1, 1 )
    VAR __End = DATE( 2024, 12, 31 )
    VAR __TotalDays = ( __End - __Start ) * 1. + 1
    
    VAR __Table = ADDCOLUMNS(
        ADDCOLUMNS(
            ADDCOLUMNS(
                'Employees',
                "__Min", IF( [Hire Date] < __Start, __Start, [Hire Date] ),
                "__Max", IF( [Term Date] > __End, __End, [Term Date] )
            ),
            "__Days", ( [__Max] - [__Min] ) + 1
        ),
        "__Percent", DIVIDE( [__Days], __TotalDays, 0 ),
        "__FullyLoadedCost", [Annual Salary] * DIVIDE( [__Days], __TotalDays, 0 ) * __LoadedCostFactor,
        "__FTE", 1 * DIVIDE( [__Days], __TotalDays, 0 )
    )
    
    VAR __EmploymentCosts = SUMX( __Table, [__FullyLoadedCost] )
    VAR __FTE = SUMX( __Table, [__FTE] )
    
    VAR __Result = DIVIDE( __Revenue - ( __TotalCost - __EmploymentCosts ), __FTE, 0 )
    RETURN __Result
```

---

## Absenteeism Rate

Percentage of expected work time lost to unplanned absences.

```dax
Absenteeism Rate = 
    VAR __Start = MIN( 'Dates'[Date] )
    VAR __End = MAX( 'Dates'[Date] )
    VAR __EmployeeContext = DISTINCT( 'Employees'[Employee] )
    
    // Calculate total available work days
    VAR __Employees = ADDCOLUMNS(
        FILTER( ALL( 'Employees' ),
            [Employee] IN __EmployeeContext &&
            [Hire Date] <= __End &&
            [Term Date] >= __Start
        ),
        "__Min", MAX( __Start, [Hire Date] ),
        "__Max", MIN( __End, [Term Date] ),
        "__WorkDays", NETWORKDAYS( MAX( __Start, [Hire Date] ), MIN( __End, [Term Date] ) )
    )
    VAR __TotalDays = SUMX( __Employees, [__WorkDays] )
    
    // Calculate absence days
    VAR __Absences = ADDCOLUMNS(
        FILTER( ALL( 'Absences' ),
            [Employee] IN __EmployeeContext &&
            [Start Date] <= __End &&
            [End Date] >= __Start
        ),
        "__Min", MAX( __Start, [Start Date] ),
        "__Max", MIN( __End, [End Date] ),
        "__WorkDays", NETWORKDAYS( MAX( __Start, [Start Date] ), MIN( __End, [End Date] ) )
    )
    VAR __AbsentDays = SUMX( __Absences, [__WorkDays] )
    
    RETURN DIVIDE( __AbsentDays, __TotalDays, 0 ) + 0
```
