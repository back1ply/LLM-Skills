# DAX Debugging Techniques

Reference file for debugging tools, techniques, and common error fixes.

## Tools

1. **DAX Studio** - Query plan analysis, performance analyzer
2. **Tabular Editor 3** - DAX debugger with breakpoints, watch windows
3. **Variables** - Return intermediate values for inspection

## Debug with Variables

```dax
Debug Measure =
VAR Step1 = SUM(Sales[Amount])
VAR Step2 = CALCULATE(Step1, ALL(Products))
VAR Step3 = DIVIDE(Step1, Step2)
-- RETURN Step1  -- Debug: Check Step1
-- RETURN Step2  -- Debug: Check Step2
RETURN Step3     -- Final result
```

## Common Errors & Fixes

| Error | Cause | Fix |
| ------- | ------- | ----- |
| Circular dependency | Column references itself in chain | Break loop with different table/approach |
| Column doesn't exist | Typo or wrong table reference | Verify against live schema extraction |
| Division by zero | No safeguard | Use `DIVIDE()` instead of `/` |
| Context transition issue | Measure called in iterator | Cache with VAR outside iterator |
| Function doesn't exist | Excel/SQL function used | Check against DAX function reference |

## Common Mistakes to Avoid

1. **Using Excel formulas** in DAX (SUMIF, VLOOKUP)
2. **Filtering tables** instead of columns
3. **Not using variables** for repeated calculations
4. **Forgetting date table** requirements for time intelligence
5. **Using IFERROR** instead of designing away errors
6. **Creating measures that never return BLANK**
7. **Using deprecated EARLIER** instead of VAR
8. **Complex logic in iterators** instead of pre-filtering
9. **Not extracting live schema** before writing DAX
10. **Ignoring context transition** performance costs
