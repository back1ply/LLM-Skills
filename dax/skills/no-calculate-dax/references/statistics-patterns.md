# Statistical Patterns

Advanced statistical calculations using the No CALCULATE approach.

---

## Linear Interpolation

> [!NOTE]
> This is an **advanced gap-filling implementation** that interpolates missing values across a sparse dataset. For a simpler point-to-point interpolation between two known values, see [Number Patterns: Linear Interpolation](./number-patterns.md#linear-interpolation).

Fill missing values by estimating between known points.

### Basic Linear Interpolation (Gap Fill)

```dax
Interpolated Value =
    VAR __CurrentDate = MAX( 'Calendar'[Date] )
    VAR __CurrentValue = MAXX(
        FILTER( 'Data', [Date] = __CurrentDate ),
        [Value]
    )

    -- If value exists, return it
    VAR __Result = IF(
        NOT( ISBLANK( __CurrentValue ) ),
        __CurrentValue,

        -- Otherwise interpolate
        VAR __PrevDate = MAXX(
            FILTER( ALL( 'Data' ), [Date] < __CurrentDate && NOT( ISBLANK( [Value] ) ) ),
            [Date]
        )
        VAR __NextDate = MINX(
            FILTER( ALL( 'Data' ), [Date] > __CurrentDate && NOT( ISBLANK( [Value] ) ) ),
            [Date]
        )
        VAR __PrevValue = MAXX( FILTER( ALL( 'Data' ), [Date] = __PrevDate ), [Value] )
        VAR __NextValue = MAXX( FILTER( ALL( 'Data' ), [Date] = __NextDate ), [Value] )

        VAR __DateRange = __NextDate - __PrevDate
        VAR __DateOffset = __CurrentDate - __PrevDate
        VAR __ValueRange = __NextValue - __PrevValue

        VAR __Interpolated = __PrevValue + ( __ValueRange * DIVIDE( __DateOffset, __DateRange, 0 ) )

        RETURN __Interpolated
    )
    RETURN __Result
```

---

## Linear Regression

Calculate trend line slope, intercept, and R-squared.

### Slope (Correlation Coefficient)

```dax
Slope =
    VAR __Data = ADDCOLUMNS(
        SUMMARIZE( 'Sales', 'Calendar'[Date] ),
        "__X", DATEDIFF( DATE( 2020, 1, 1 ), [Date], DAY ),
        "__Y", [Sales]
    )
    VAR __N = COUNTROWS( __Data )
    VAR __SumX = SUMX( __Data, [__X] )
    VAR __SumY = SUMX( __Data, [__Y] )
    VAR __SumXY = SUMX( __Data, [__X] * [__Y] )
    VAR __SumX2 = SUMX( __Data, [__X] * [__X] )

    VAR __Slope = DIVIDE(
        ( __N * __SumXY ) - ( __SumX * __SumY ),
        ( __N * __SumX2 ) - ( __SumX * __SumX ),
        0
    )
    RETURN __Slope
```

### Intercept

```dax
Intercept =
    VAR __Data = ADDCOLUMNS(
        SUMMARIZE( 'Sales', 'Calendar'[Date] ),
        "__X", DATEDIFF( DATE( 2020, 1, 1 ), [Date], DAY ),
        "__Y", [Sales]
    )
    VAR __N = COUNTROWS( __Data )
    VAR __MeanX = AVERAGEX( __Data, [__X] )
    VAR __MeanY = AVERAGEX( __Data, [__Y] )
    VAR __Slope = [Slope]

    VAR __Intercept = __MeanY - ( __Slope * __MeanX )
    RETURN __Intercept
```

### Trend Line Forecast

```dax
Trend Forecast =
    VAR __CurrentDate = MAX( 'Calendar'[Date] )
    VAR __X = DATEDIFF( DATE( 2020, 1, 1 ), __CurrentDate, DAY )
    VAR __Predicted = [Intercept] + ( [Slope] * __X )
    RETURN __Predicted
```

### R-Squared (Coefficient of Determination)

Measures how well the trend line fits the data (0 to 1):

```dax
R-Squared =
    VAR __Data = ADDCOLUMNS(
        SUMMARIZE( 'Sales', 'Calendar'[Date] ),
        "__X", DATEDIFF( DATE( 2020, 1, 1 ), [Date], DAY ),
        "__Y", [Sales],
        "__Predicted", [Intercept] + ( [Slope] * DATEDIFF( DATE( 2020, 1, 1 ), [Date], DAY ) )
    )

    VAR __MeanY = AVERAGEX( __Data, [__Y] )

    -- Sum of squared residuals
    VAR __SSRes = SUMX( __Data, POWER( [__Y] - [__Predicted], 2 ) )

    -- Total sum of squares
    VAR __SSTot = SUMX( __Data, POWER( [__Y] - __MeanY, 2 ) )

    VAR __RSquared = 1 - DIVIDE( __SSRes, __SSTot, 0 )
    RETURN __RSquared
```

**Interpretation:**
- R² = 1: Perfect fit
- R² = 0.9: Very strong fit
- R² = 0.7: Moderate fit
- R² < 0.5: Weak fit

---

## Correlation

Measure relationship strength between two variables.

### Pearson Correlation Coefficient

```dax
Correlation =
    VAR __Data = ADDCOLUMNS(
        'Sales',
        "__X", [Price],
        "__Y", [Quantity]
    )
    VAR __N = COUNTROWS( __Data )
    VAR __SumX = SUMX( __Data, [__X] )
    VAR __SumY = SUMX( __Data, [__Y] )
    VAR __SumXY = SUMX( __Data, [__X] * [__Y] )
    VAR __SumX2 = SUMX( __Data, [__X] * [__X] )
    VAR __SumY2 = SUMX( __Data, [__Y] * [__Y] )

    VAR __Numerator = ( __N * __SumXY ) - ( __SumX * __SumY )
    VAR __DenomX = ( __N * __SumX2 ) - ( __SumX * __SumX )
    VAR __DenomY = ( __N * __SumY2 ) - ( __SumY * __SumY )

    VAR __Correlation = DIVIDE(
        __Numerator,
        SQRT( __DenomX * __DenomY ),
        0
    )
    RETURN __Correlation
```

**Interpretation:**
- +1: Perfect positive correlation
- 0: No correlation
- -1: Perfect negative correlation
- |r| > 0.7: Strong correlation
- |r| < 0.3: Weak correlation

---

## Percentiles

> [!IMPORTANT]
> **For most use cases, use the native `PERCENTILEX.INC` or `PERCENTILEX.EXC` functions** shown in [Number Patterns](./number-patterns.md#statistical-aggregations). The custom implementation below is provided for:
> - Educational purposes (understanding percentile calculation logic)
> - Legacy models where native functions aren't available
> - Specific edge cases requiring custom ranking behavior

Calculate percentile values (P50, P75, P90, P95, P99).

### Percentile Calculation

```dax
Percentile 90 =
    VAR __Percentile = 0.90
    VAR __Sorted = ADDCOLUMNS(
        SUMMARIZE( 'Sales', 'Sales'[OrderID] ),
        "__Value", [Amount],
        "__Rank", RANKX( ALL( 'Sales' ), [Amount], , ASC, DENSE )
    )
    VAR __Count = COUNTROWS( __Sorted )
    VAR __Position = __Percentile * ( __Count + 1 )
    VAR __LowerRank = INT( __Position )
    VAR __UpperRank = __LowerRank + 1
    VAR __Fraction = __Position - __LowerRank

    VAR __LowerValue = MAXX( FILTER( __Sorted, [__Rank] = __LowerRank ), [__Value] )
    VAR __UpperValue = MAXX( FILTER( __Sorted, [__Rank] = __UpperRank ), [__Value] )

    VAR __Result = __LowerValue + ( __Fraction * ( __UpperValue - __LowerValue ) )
    RETURN __Result
```

### Generic Percentile Function

```dax
Percentile =
    VAR __P = 0.95  -- Change this value for different percentiles
    VAR __Values = SUMMARIZE( 'Sales', 'Sales'[OrderID], "__Val", [Amount] )
    VAR __Sorted = ADDCOLUMNS(
        __Values,
        "__Rank", RANKX( __Values, [__Val], , ASC )
    )
    VAR __N = COUNTROWS( __Sorted )
    VAR __Pos = __P * ( __N + 1 )
    VAR __Lower = INT( __Pos )
    VAR __Upper = __Lower + 1
    VAR __Frac = __Pos - __Lower

    VAR __LVal = MAXX( FILTER( __Sorted, [__Rank] = __Lower ), [__Val] )
    VAR __UVal = MAXX( FILTER( __Sorted, [__Rank] = __Upper ), [__Val] )

    RETURN __LVal + ( __Frac * ( __UVal - __LVal ) )
```

---

## Quartiles & IQR

### Quartile Calculations

```dax
Q1 (25th Percentile) = [Use Percentile with 0.25]
Q2 (Median) = MEDIAN( 'Sales'[Amount] )
Q3 (75th Percentile) = [Use Percentile with 0.75]
```

### Interquartile Range (IQR)

```dax
IQR =
    VAR __Q1 = [Q1]
    VAR __Q3 = [Q3]
    RETURN __Q3 - __Q1
```

### Outlier Detection

Values outside 1.5 × IQR from Q1/Q3:

```dax
Outliers =
    VAR __Q1 = [Q1]
    VAR __Q3 = [Q3]
    VAR __IQR = __Q3 - __Q1
    VAR __LowerFence = __Q1 - ( 1.5 * __IQR )
    VAR __UpperFence = __Q3 + ( 1.5 * __IQR )

    VAR __Table = FILTER(
        'Sales',
        [Amount] < __LowerFence || [Amount] > __UpperFence
    )
    RETURN COUNTROWS( __Table )
```

---

## Standard Deviation & Variance

### Population Standard Deviation

```dax
Std Dev =
    VAR __Data = 'Sales'[Amount]
    VAR __Mean = AVERAGE( __Data )
    VAR __SumSquaredDiff = SUMX( 'Sales', POWER( [Amount] - __Mean, 2 ) )
    VAR __Count = COUNTROWS( 'Sales' )
    VAR __Variance = DIVIDE( __SumSquaredDiff, __Count, 0 )
    VAR __StdDev = SQRT( __Variance )
    RETURN __StdDev
```

Or use built-in:
```dax
Std Dev = STDEV.P( 'Sales'[Amount] )  -- Population
Std Dev Sample = STDEV.S( 'Sales'[Amount] )  -- Sample
```

### Coefficient of Variation

Standard deviation as percentage of mean:

```dax
Coefficient of Variation =
    VAR __StdDev = STDEV.P( 'Sales'[Amount] )
    VAR __Mean = AVERAGE( 'Sales'[Amount] )
    RETURN DIVIDE( __StdDev, __Mean, 0 )
```

### TRIMMEAN (Excel Equivalent)

Calculates the mean of the interior of a data set. TRIMMEAN excludes a percentage of data points from the top and bottom tails.

```dax
TRIMMEAN = 
    VAR __Table = ALL( 'Sales' )
    VAR __N = COUNTROWS ( __Table ) 
    VAR __K = 0.2 // Percentage to trim (e.g., 20%)
    VAR __NumToTrim = ROUND ( __N * __K / 2, 0 ) 
    VAR __RankedTable = ADDCOLUMNS( 
        __Table, 
        "__Rank", RANKX ( __Table, [Amount], , ASC ) 
    ) 
    VAR __TrimmedTable = FILTER ( 
        __RankedTable, 
        [__Rank] > __NumToTrim && [__Rank] <= __N - __NumToTrim 
    ) 
    VAR __Result = AVERAGEX ( __TrimmedTable, [Amount] ) 
    RETURN __Result
```

---

## Z-Score (Standardization)

Measure how many standard deviations from mean:

```dax
Z-Score =
    VAR __Value = MAX( 'Sales'[Amount] )
    VAR __Mean = AVERAGEX( ALL( 'Sales' ), [Amount] )
    VAR __StdDev = STDEVX.P( ALL( 'Sales' ), [Amount] )
    VAR __ZScore = DIVIDE( __Value - __Mean, __StdDev, 0 )
    RETURN __ZScore
```

**Interpretation:**
- Z > 2: More than 2 std devs above mean (unusual high)
- -2 < Z < 2: Within normal range
- Z < -2: More than 2 std devs below mean (unusual low)

---

## Moving Statistics

### Moving Average

```dax
Moving Average 3 Period =
    VAR __CurrentDate = MAX( 'Calendar'[Date] )
    VAR __PreviousDates = FILTER(
        ALL( 'Calendar' ),
        [Date] <= __CurrentDate &&
        [Date] > __CurrentDate - 90  -- 3 months ~90 days
    )
    VAR __Table = SUMMARIZE(
        __PreviousDates,
        [Date],
        "__Value", [Sales]
    )
    RETURN AVERAGEX( __Table, [__Value] )
```

### Moving Standard Deviation

```dax
Moving Std Dev =
    VAR __CurrentDate = MAX( 'Calendar'[Date] )
    VAR __Window = FILTER(
        ALL( 'Sales' ),
        [Date] <= __CurrentDate &&
        [Date] > __CurrentDate - 90
    )
    RETURN STDEVX.P( __Window, [Amount] )
```

---

## Exponential Smoothing

Simple exponential smoothing for forecasting:

```dax
Exponentially Smoothed =
    VAR __Alpha = 0.3  -- Smoothing factor (0 to 1)
    VAR __CurrentDate = MAX( 'Calendar'[Date] )

    VAR __Data = ADDCOLUMNS(
        FILTER( ALL( 'Calendar' ), [Date] <= __CurrentDate ),
        "__Value", [Sales],
        "__DateNum", DATEDIFF( DATE( 2020, 1, 1 ), [Date], DAY )
    )

    VAR __Result = SUMX(
        __Data,
        [__Value] * POWER( 1 - __Alpha, MAX( [__DateNum] ) - [__DateNum] )
    ) / SUMX(
        __Data,
        POWER( 1 - __Alpha, MAX( [__DateNum] ) - [__DateNum] )
    )

    RETURN __Result
```

---

## Distribution Analysis

### Skewness

Measure asymmetry of distribution:

```dax
Skewness =
    VAR __Data = 'Sales'
    VAR __Mean = AVERAGE( [Amount] )
    VAR __StdDev = STDEV.P( [Amount] )
    VAR __N = COUNTROWS( __Data )

    VAR __Sum3rdMoment = SUMX(
        __Data,
        POWER( DIVIDE( [Amount] - __Mean, __StdDev, 0 ), 3 )
    )

    VAR __Skewness = DIVIDE( __Sum3rdMoment, __N, 0 )
    RETURN __Skewness
```

**Interpretation:**
- Skew = 0: Symmetric (normal distribution)
- Skew > 0: Right-skewed (long tail on right)
- Skew < 0: Left-skewed (long tail on left)

### Kurtosis

Measure "tailedness" of distribution:

```dax
Kurtosis =
    VAR __Data = 'Sales'
    VAR __Mean = AVERAGE( [Amount] )
    VAR __StdDev = STDEV.P( [Amount] )
    VAR __N = COUNTROWS( __Data )

    VAR __Sum4thMoment = SUMX(
        __Data,
        POWER( DIVIDE( [Amount] - __Mean, __StdDev, 0 ), 4 )
    )

    VAR __Kurtosis = DIVIDE( __Sum4thMoment, __N, 0 ) - 3
    RETURN __Kurtosis
```

**Interpretation:**
- Kurt = 0: Normal distribution
- Kurt > 0: Heavy tails (more outliers)
- Kurt < 0: Light tails (fewer outliers)

---

## Confidence Intervals

### 95% Confidence Interval for Mean

```dax
CI Lower 95% =
    VAR __Mean = AVERAGE( 'Sales'[Amount] )
    VAR __StdDev = STDEV.S( 'Sales'[Amount] )
    VAR __N = COUNTROWS( 'Sales' )
    VAR __StdError = DIVIDE( __StdDev, SQRT( __N ), 0 )
    VAR __ZScore = 1.96  -- For 95% confidence
    RETURN __Mean - ( __ZScore * __StdError )

CI Upper 95% =
    VAR __Mean = AVERAGE( 'Sales'[Amount] )
    VAR __StdDev = STDEV.S( 'Sales'[Amount] )
    VAR __N = COUNTROWS( 'Sales' )
    VAR __StdError = DIVIDE( __StdDev, SQRT( __N ), 0 )
    VAR __ZScore = 1.96  -- For 95% confidence
    RETURN __Mean + ( __ZScore * __StdError )
```

---

## Weighted Statistics

> **Note**: Weighted Average and Weighted Standard Deviation patterns have been consolidated into [Number Patterns](./number-patterns.md).

## Growth Rate Calculations

### Compound Annual Growth Rate (CAGR)

```dax
CAGR =
    VAR __StartValue = [Sales First Year]
    VAR __EndValue = [Sales Last Year]
    VAR __Years = DISTINCTCOUNT( 'Calendar'[Year] ) - 1
    VAR __CAGR = POWER( DIVIDE( __EndValue, __StartValue, 1 ), 1 / __Years ) - 1
    RETURN __CAGR
```

### Average Growth Rate

```dax
Average Growth Rate =
    VAR __Data = ADDCOLUMNS(
        SUMMARIZE( 'Sales', 'Calendar'[Year] ),
        "__Value", [Sales],
        "__PrevValue", [Sales PY]
    )
    VAR __GrowthRates = ADDCOLUMNS(
        FILTER( __Data, NOT( ISBLANK( [__PrevValue] ) ) ),
        "__GrowthRate", DIVIDE( [__Value] - [__PrevValue], [__PrevValue], 0 )
    )
    RETURN AVERAGEX( __GrowthRates, [__GrowthRate] )
```

---

## Statistical Tests

### Coefficient of Determination (for actual vs forecast)

```dax
Forecast Accuracy =
    VAR __Data = ADDCOLUMNS(
        'Sales',
        "__Actual", [Actual Sales],
        "__Forecast", [Forecast Sales]
    )
    VAR __MeanActual = AVERAGEX( __Data, [__Actual] )

    VAR __SSRes = SUMX( __Data, POWER( [__Actual] - [__Forecast], 2 ) )
    VAR __SSTot = SUMX( __Data, POWER( [__Actual] - __MeanActual, 2 ) )

    RETURN 1 - DIVIDE( __SSRes, __SSTot, 0 )
```

---

## Performance Notes

Statistical calculations can be computationally expensive:

1. **Filter early**: Reduce data before statistical calculations
2. **Use variables**: Cache intermediate results
3. **Avoid row-by-row**: Summarize first when possible
4. **Consider grain**: Statistical measures at appropriate aggregation level

---

## See Also

- [Number Patterns](number-patterns.md) - Basic aggregations, ranking
- [Time Intelligence](time-intelligence.md) - Rolling averages
- [Advanced & Complex Patterns](advanced-complex-patterns.md) - Complex calculations
