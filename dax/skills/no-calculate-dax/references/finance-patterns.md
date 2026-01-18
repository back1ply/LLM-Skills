# Finance Patterns

Common finance calculations using the No CALCULATE approach.

## Gross Margin

```dax
Gross Margin % =
    VAR __Revenue = SUMX( 'Sales', [Quantity] * [Price] )
    VAR __Cost = SUMX( 'Sales', [Quantity] * [Cost] )
    VAR __Margin = __Revenue - __Cost
    RETURN DIVIDE( __Margin, __Revenue, 0 )
```

---

## Budget Variance

```dax
Budget Variance % =
    VAR __Actuals = SUM( 'Actuals'[Amount] )
    VAR __Budget = SUM( 'Budget'[Amount] )
    RETURN DIVIDE( __Actuals - __Budget, __Budget, 0 )
```

### With Favorable/Unfavorable Indicator

```dax
Budget Variance Status =
    VAR __Variance = [Budget Variance %]
    RETURN SWITCH(
        TRUE(),
        __Variance > 0.05, "Favorable",
        __Variance < -0.05, "Unfavorable",
        "On Track"
    )
```

---

## Currency Conversion

```dax
Revenue USD =
    VAR __Table = ADDCOLUMNS( 'Sales',
        "__USD", [Amount] * MAXX(
            FILTER( 'Rates', [Currency] = EARLIER( 'Sales'[Currency] ) ), [Rate] ) )
    RETURN SUMX( __Table, [__USD] )
```

### With Date-Based Rates

```dax
Revenue USD Historical =
    VAR __Table = ADDCOLUMNS( 'Sales',
        "__USD", [Amount] * MAXX(
            FILTER( 'Rates', 
                [Currency] = EARLIER( 'Sales'[Currency] ) && 
                [Date] = EARLIER( 'Sales'[Date] ) 
            ), [Rate] ) )
    RETURN SUMX( __Table, [__USD] )
```

---

## Reverse Year-To-Date

Convert YTD values back to monthly:

```dax
Monthly From YTD =
    VAR __CurrentYTD = [YTD Amount]
    VAR __PreviousMonthYTD = [Previous Month YTD Amount]
    RETURN __CurrentYTD - __PreviousMonthYTD
```

---

## Accounts Payable Turnover Ratio

```dax
AP Turnover Ratio =
    VAR __Purchases = SUM( 'Purchases'[Amount] )
    VAR __AvgPayables = DIVIDE( 
        SUM( 'Payables'[BeginningBalance] ) + SUM( 'Payables'[EndingBalance] ), 
        2 
    )
    RETURN DIVIDE( __Purchases, __AvgPayables, 0 )
```

---

## Compound Interest

```dax
Future Value =
    VAR __Principal = [Initial Amount]
    VAR __Rate = [Interest Rate]
    VAR __Periods = [Number of Periods]
    RETURN __Principal * POWER( 1 + __Rate, __Periods )
```

---

## Modified Dietz Return

Time-weighted return calculation for investment portfolios with cash flows:

```dax
Modified Dietz Return = 
    VAR __StartValue = SUM( 'Portfolio'[Beginning Value] )
    VAR __EndValue = SUM( 'Portfolio'[Ending Value] )
    VAR __PeriodDays = MAX( 'Portfolio'[Total Days] )
    
    VAR __CashFlows = SUMX( 'Transactions', [Amount] )
    VAR __WeightedFlows = SUMX( 
        'Transactions', 
        [Amount] * DIVIDE( __PeriodDays - [Days Since Start], __PeriodDays, 0 )
    )
    
    VAR __Result = DIVIDE( 
        __EndValue - __StartValue - __CashFlows, 
        __StartValue + __WeightedFlows,
        0
    )
    RETURN __Result
```

> **Use case**: Measures portfolio performance adjusted for the timing of deposits/withdrawals.

---

## Accounts Payable Days

How long it takes to pay suppliers (Days Payable Outstanding):

```dax
AP Days = 
    VAR __Turnover = [AP Turnover Ratio]
    VAR __Result = DIVIDE( 365, __Turnover, 0 )
    RETURN __Result
```

---

## Periodic Billing / Amortization

Spread annual amount over months (Revenue Recognition):

```dax
Monthly Revenue = 
    VAR __Billings = ADDCOLUMNS( 
        'Periodic Billing', 
        "__YMBegin", YEAR( [BeginDate] ) * 100 + MONTH( [BeginDate] ), 
        "__YMEnd", YEAR( [EndDate] ) * 100 + MONTH( [EndDate] ) 
    ) 
    VAR __Table = SELECTCOLUMNS( 
        GENERATE( 
            __Billings, 
            SUMMARIZE( 
                FILTER( 'Dates', [YM Sort] >= [__YMBegin] && [YM Sort] <= [__YMEnd] ), 
                [YM Sort] 
            ) 
        ), 
        "Amount", [Amount] 
    ) 
    VAR __Result = SUMX( __Table, [Amount] ) 
    RETURN __Result
```

> **Note**: This pattern uses `GENERATE` to create a row for every month a subscription is active, allowing for accurate monthly revenue reporting without complex logic.
