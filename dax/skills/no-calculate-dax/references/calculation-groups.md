# Calculation Groups Strategy

Integrating standard Calculation Groups while minimizing `CALCULATE` reliance.

## The Challenge

Calculation Groups predominantly use `CALCULATE( SELECTEDMEASURE(), ... )` to apply logic. This seems to violate the "No CALCULATE" rule.

**Exception Policy**: Calculation Groups are **Infrastructure**, not Business Logic. Using `CALCULATE` inside a Calculation Item to shift context is acceptable *if and only if* the underlying measures being selected are robust "No CALCULATE" measures.

> **See also**: [Philosophy: When CALCULATE May Be Acceptable](./philosophy.md#when-calculate-may-be-acceptable) for the full rationale behind this exception.

However, we can still write Calculation Items more explicitly.

---

## Pattern 1: Time Intelligence Items

Instead of relying largely on `DATESYTD`, use standard Time Intelligence functions only as "Context Shifters" and let the Measure handle the aggregation.

### Standard Approach (Mixed)

```dax
Item "YTD" = 
    CALCULATE( 
        SELECTEDMEASURE(), 
        DATESYTD( 'Calendar'[Date] ) 
    )
```

### No-CALCULATE Hybrid Approach

If your base measures are written with the Variable Pattern, they expect a Filter Context.

```dax
Item "YTD" = 
    VAR __MaxDate = MAX( 'Calendar'[Date] )
    VAR __Year = YEAR( __MaxDate )
    RETURN
        CALCULATE(
            SELECTEDMEASURE(),
            'Calendar'[Year] = __Year,
            'Calendar'[Date] <= __MaxDate
        )
```

*Note: This is cleaner because it makes the specific filter logic explicit (Year = Year AND Date <= MaxDate) rather than relying on the black box of `DATESYTD`.*

---

## Pattern 2: Currency Conversion

Avoid `CALCULATE` entirely by using iteration logic on the result of the measure, if applicable.

```dax
Item "USD Conversion" = 
    VAR __Rate = LOOKUPVALUE( 'Rates'[Rate], 'Rates'[Currency], "USD" )
    VAR __Value = SELECTEDMEASURE()
    RETURN __Value * __Rate
```

---

## Pattern 3: Measure Overrides

Sometimes you want a Calculation Item to completely replace the measure logic (e.g., "Margin %").

### explicit Logic

```dax
Item "Margin %" = 
    VAR __Revenue = 
        CALCULATE( 
            SELECTEDMEASURE(), 
            'MeasureMetadata'[Name] = "Total Revenue" -- Virtual switch
        )
    VAR __Cost = 
        CALCULATE( 
            SELECTEDMEASURE(), 
            'MeasureMetadata'[Name] = "Total Cost"
        )
    RETURN DIVIDE( __Revenue - __Cost, __Revenue, 0 )
```

---

## Best Practices

1.  **Keep Items Simple**: Don't put complex business logic in Calculation Items. Put it in the Measures.
2.  **Use Explicit Filters**: Even inside `CALCULATE` in a Calc Item, write out the boolean filters `( 'Date'[Year] = 2024 )` instead of using Time Intel sugar syntax.
3.  **Validate Context**: Ensure your base measures (Variable Pattern) don't have hard-coded filters that conflict with the Calculation Group's injected context.
