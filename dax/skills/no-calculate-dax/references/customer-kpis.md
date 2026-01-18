# Customer KPIs

Common customer metrics using the No CALCULATE approach.

## New Customers

Customers appearing for the first time in the current period:

```dax
New Customers =
    VAR __Date = MIN( 'Dates'[Date] )
    VAR __Current = DISTINCT( 'Customers'[ID] )
    VAR __Previous = DISTINCT( SELECTCOLUMNS(
        FILTER( ALL( 'Customers' ), [Date] < __Date ), "ID", [ID] ) )
    VAR __Table = EXCEPT( __Current, __Previous )
    RETURN COUNTROWS( __Table ) + 0
```

> The `+ 0` ensures BLANK returns as 0 instead of blank.

---

## Lost Customers

Customers who purchased last period but not this period:

```dax
Lost Customers =
    VAR __Date = MIN( 'Dates'[Date] )
    VAR __Current = DISTINCT( 'Customers'[ID] )
    VAR __Previous = DISTINCT( SELECTCOLUMNS(
        FILTER( ALL( 'Customers' ), [Date] > EOMONTH( __Date, -2 ) && [Date] < __Date ),
        "ID", [ID] ) )
    RETURN COUNTROWS( EXCEPT( __Previous, __Current ) ) + 0
```

---

## Net Promoter Score (NPS)

Survey-based metric from -100 to 100.

- Scores 0-6 = Detractors
- Scores 7-8 = Passives (ignored)
- Scores 9-10 = Promoters

```dax
NPS =
    VAR __Table = ALL( 'Survey' )
    VAR __Total = COUNTROWS( __Table )
    VAR __Detractors = COUNTROWS( FILTER( __Table, [Score] < 7 ) )
    VAR __Promoters = COUNTROWS( FILTER( __Table, [Score] > 8 ) )
    RETURN ( DIVIDE( __Promoters, __Total ) - DIVIDE( __Detractors, __Total ) ) * 100
```

---

## Churn Rate

Percentage of customers lost:

```dax
Churn Rate = 
    VAR __MinDate = MIN( 'Dates'[Date] )
    VAR __PMStart = EOMONTH( __MinDate, -2 ) + 1
    VAR __PMEnd = EOMONTH( __MinDate, -1 )
    VAR __Customers = DISTINCT( 'Customers'[ID] )
    VAR __PMCustomers = DISTINCT( SELECTCOLUMNS( 
        FILTER( ALL( 'Customers' ), [Date] >= __PMStart && [Date] <= __PMEnd ), 
        "ID", [ID] ) )
    VAR __CMCustomers = INTERSECT( __Customers, __PMCustomers )
    VAR __PMCount = COUNTROWS( __PMCustomers )
    VAR __TotalLost = __PMCount - COUNTROWS( __CMCustomers )
    RETURN DIVIDE( __TotalLost, __PMCount, BLANK() )
```

---

## Growth Rate

Percentage of new customers acquired relative to previous period:

```dax
Growth Rate = 
    VAR __MinDate = MIN( 'Dates'[Date] )
    VAR __PMStart = EOMONTH( __MinDate, -2 ) + 1
    VAR __PMEnd = EOMONTH( __MinDate, -1 )
    VAR __Customers = DISTINCT( 'Customers'[ID] )
    VAR __PMCustomers = DISTINCT( SELECTCOLUMNS( 
        FILTER( ALL( 'Customers' ), [Date] >= __PMStart && [Date] <= __PMEnd ), 
        "ID", [ID] ) )
    VAR __NewCustomers = EXCEPT( __Customers, __PMCustomers )
    VAR __PMCount = COUNTROWS( __PMCustomers )
    VAR __NewCount = COUNTROWS( __NewCustomers )
    RETURN DIVIDE( __NewCount, __PMCount, BLANK() )
```

---

## Customer Retention Rate

```dax
Retention Rate = 1 - [Churn Rate]
```

---

## Customer Lifetime Value (CLV)

Simple CLV calculation:

```dax
Customer Lifetime Value = 
    VAR __Customers = COUNTROWS( DISTINCT( 'Sales'[CustomerID] ) )
    VAR __MinDate = MIN( 'Sales'[Date] )
    VAR __MaxDate = MAX( 'Sales'[Date] )
    VAR __Years = IF( ( __MaxDate - __MinDate ) < 366, 1, YEAR( __MaxDate ) - YEAR( __MinDate ) + 1 )
    VAR __AvgPurchaseFrequency = DIVIDE( COUNTROWS( 'Sales' ), __Years, BLANK() )
    VAR __AvgPurchaseValue = AVERAGE( 'Sales'[Amount] )
    VAR __AvgCustomerValue = __AvgPurchaseValue * __AvgPurchaseFrequency
    VAR __AvgCustomerLifespan = 1 / [Churn Rate]
    RETURN DIVIDE( __AvgCustomerValue * __AvgCustomerLifespan, __Customers, BLANK() )
```

---

## Returning Customers

Customers who have purchased more than once:

```dax
Returning Customers =
    VAR __Table = FILTER(
        SUMMARIZE( 'Sales', 'Sales'[CustomerID], "__Count", COUNTROWS( 'Sales' ) ),
        [__Count] > 1
    )
    RETURN COUNTROWS( __Table )
```

---

## Customer Acquisition Cost (CAC)

Cost per customer acquired from marketing campaigns:

```dax
CAC = 
    VAR __Table = ADDCOLUMNS( 
        'Campaigns', 
        "__Cost", [Clicks] * [Cost Per Click] 
    )
    VAR __Customers = SUMX( __Table, [New Customers] )
    VAR __Cost = SUMX( __Table, [__Cost] )
    VAR __Result = DIVIDE( __Cost, __Customers )
    RETURN __Result
```

---

## Open Tickets (at a point in time)

Count tickets open on a given date (tickets that span multiple days):

```dax
Tickets Open = 
    VAR __Tickets = ADDCOLUMNS(
        'Tickets',
        "__EffectiveDate", IF( ISBLANK( [Closed Date] ), TODAY(), [Closed Date] )
    )
    VAR __Table = SELECTCOLUMNS(
        GENERATE(
            __Tickets,
            FILTER( 'Dates', [Date] >= [Opened Date] && [Date] <= [__EffectiveDate] )
        ),
        "__ID", [Ticket Num]
    )
    VAR __Result = COUNTROWS( __Table )
    RETURN __Result
```

> **Performance Note**: For large datasets, use this optimized pattern (Patron Recommendation):
> ```dax
> VAR __CurrDate = MAX( 'Dates'[Date] ) 
> VAR __Table = FILTER( 
>     'Tickets', 
>     __CurrDate >= [Opened Date] && __CurrDate <= [__EffectiveDate] 
> )
> RETURN COUNTROWS( __Table )
> ```

---

## Average Time to Close

```dax
Avg Time to Close = 
    VAR __Table = ADDCOLUMNS(
        FILTER( 'Tickets', NOT( ISBLANK( [Closed Date] ) ) ),
        "__Days", [Closed Date] - [Opened Date] + 1
    )
    VAR __Result = AVERAGEX( __Table, [__Days] )
    RETURN __Result
```

---

## Funnel Drop-off Rate

Percentage of customers lost at each funnel step:

```dax
Drop-off Rate = 
    VAR __CurrStep = MAX( 'Funnel'[Step] )
    VAR __PrevStep = __CurrStep - 1
    VAR __CurrCount = COUNTROWS( 'Funnel' )
    VAR __PrevCount = IF( 
        __CurrStep = 1, 0, 
        COUNTROWS( FILTER( ALL( 'Funnel' ), [Step] = __PrevStep ) ) 
    )
    VAR __Result = DIVIDE( __PrevCount - __CurrCount, __PrevCount, 0 )
    RETURN __Result
```

---

## Abandonment Rate

Percentage lost relative to the first step:

```dax
Abandonment Rate = 
    VAR __CurrStep = MAX( 'Funnel'[Step] )
    VAR __FirstCount = COUNTROWS( FILTER( ALL( 'Funnel' ), [Step] = 1 ) )
    VAR __CurrCount = COUNTROWS( 'Funnel' )
    VAR __Result = DIVIDE( __FirstCount - __CurrCount, __FirstCount, 0 )
    RETURN __Result
```

---

## Market Basket Analysis

For product affinity, cross-sell recommendations, and bundle analysis, see [Market Basket Analysis](market-basket-analysis.md).

Topics covered:
- Product pairs & "Better Together" analysis
- Support, confidence, and lift calculations
- Cross-sell recommendations
- Bundle analysis
- Category affinity
- Sequence analysis & next purchase prediction
- Cannibalization analysis

---

## Annual Contract Value (ACV)

Average yearly revenue per customer contract:

```dax
ACV = 
    VAR __Table = ADDCOLUMNS( 
        'Contracts', 
        "__ACV", DIVIDE( [TCV], MAX( [Years], 1 ) ) 
    )
    VAR __Customers = COUNTROWS( 'Contracts' )
    VAR __TotalACV = SUMX( __Table, [__ACV] )
    VAR __Result = DIVIDE( __TotalACV, __Customers, 0 )
    RETURN __Result
```

---

## Sales After Event

Track sales of products after a sales visit/event:

```dax
Sales After Visit =
    VAR __VisitDate = MAX( 'Visits'[Date] )
    VAR __SalesAfter = SUMMARIZE(
        FILTER( 'Sales', [Date] > __VisitDate ),
        [Product], "__Qty", SUM( [Qty] ), "__FirstSaleDate", MIN( [Date] )
    )
    VAR __WithHistory = ADDCOLUMNS(
        __SalesAfter,
        "__LastSaleBefore",
        MAXX( FILTER( 'Sales', [Date] <= __VisitDate && [Product] = EARLIER( [Product] ) ), [Date] )
    )
    VAR __Qualified = FILTER(
        __WithHistory,
        ISBLANK( [__LastSaleBefore] ) || [__FirstSaleDate] - [__LastSaleBefore] >= 100
    )
    RETURN SUMX( __Qualified, [__Qty] )
```

---

## Cohort Analysis

### Monthly Retention Cohort

Track customer retention by signup cohort:

```dax
Cohort Retention % =
    VAR __CohortMonth = MAX( 'Cohorts'[CohortMonth] )
    VAR __CurrentMonth = MAX( 'Calendar'[Month] )

    -- Customers in this cohort
    VAR __CohortCustomers = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Customers', [SignupMonth] = __CohortMonth ),
        "__CustomerID", [CustomerID]
    ))

    -- Customers from cohort active in current month
    VAR __ActiveCustomers = INTERSECT(
        __CohortCustomers,
        DISTINCT( SELECTCOLUMNS(
            FILTER( 'Sales', [Month] = __CurrentMonth ),
            "__CustomerID", [CustomerID]
        ))
    )

    VAR __Result = DIVIDE(
        COUNTROWS( __ActiveCustomers ),
        COUNTROWS( __CohortCustomers ),
        0
    )
    RETURN __Result
```

### Cohort Revenue Trend

Total revenue by cohort over time:

```dax
Cohort Revenue =
    VAR __CohortMonth = MAX( 'Cohorts'[CohortMonth] )

    VAR __CohortCustomers = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Customers', [SignupMonth] = __CohortMonth ),
        "__CustomerID", [CustomerID]
    ))

    VAR __Table = FILTER(
        'Sales',
        [CustomerID] IN __CohortCustomers
    )

    RETURN SUMX( __Table, [Amount] )
```

### Months Since Signup

Helper column for cohort analysis:

```dax
Months Since Signup =
    VAR __SignupMonth = RELATED( 'Customers'[SignupMonth] )
    VAR __CurrentMonth = 'Sales'[Month]
    VAR __MonthsDiff = DATEDIFF( __SignupMonth, __CurrentMonth, MONTH )
    RETURN __MonthsDiff
```

---

## See Also

- [Market Basket Analysis](market-basket-analysis.md) - Product affinity patterns
- [Statistics Patterns](statistics-patterns.md) - Correlation, regression
- [Time Intelligence](time-intelligence.md) - Period comparisons
