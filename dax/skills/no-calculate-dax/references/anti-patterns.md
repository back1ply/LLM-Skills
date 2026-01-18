# Anti-Patterns

Practices to strictly avoid when following the "No CALCULATE" methodology.

## 1. Implicit Measures

Drag-and-dropping columns into visuals creates "Implicit Measures".

**Why it's bad**:
- You can't reuse logic.
- You can't format well.
- Debugging is impossible.
- It calculates *something*, but you don't control *what*.

**Fix**: Always write explicit measures (e.g., `Sum Sales = SUM('Sales'[Amount])`).

## 2. Auto Date/Time

**Why it's bad**:
- Bloats model size (creates hidden table for every date column).
- Doesn't support custom calendars (4-4-5, fiscal years).
- "Time Intelligence" functions rely on it, hiding logic.

**Fix**:
- Disable "Auto Date/Time" in Options.
- Use a dedicated `Calendar` table with `Offset` columns.

## 3. Bidirectional Cross-Filtering

Turning on "Both" direction relationships.

**Why it's bad**:
- Ambiguity: Paths become unpredictable.
- Performance: Filters verify massive paths.
- "Ambiguous Path" errors.

**Fix**: 
- Keep relationships "Single" (1->Many).
- If you *must* filter the "1" side from the "Many" side, use `CROSSFILTER` explicitly in a specific measure (or better, rethink the model).

## 4. Calculated Columns for Aggregation

```dax
// BAD: Column = SUM( 'Sales'[Amount] )
```

**Why it's bad**:
- `SUM` in a column returns the *entire table's* sum (or is context-dependent in weird ways).
- Takes up RAM.
- Static (doesn't change with slicers).

**Fix**: Use a Measure for aggregation. Calculated columns should only be used for static row-level calculations (sorting, filtering, or relationship keys). See [Beginner Concepts: When to Use Calculated Columns](./beginner-concepts.md#when-to-use-calculated-columns) for valid use cases.

## 5. Filtering Entire Tables

**Bad**:
```dax
FILTER( 'Sales', 'Sales'[Color] = "Red" )
```

**Why it's bad**: It scans the entire wide fact table.

**Better**: Iterate only on what you need.
```dax
// Context transition handled by variables usually, but if aggregating:
SUMX( FILTER( 'Sales', 'Sales'[Color] = "Red" ), [Amount] )
```

**Best (Star Schema)**:
Filter the Dimension, not the Fact.
```dax
VAR __DimFilter = FILTER( 'Product', 'Product'[Color] = "Red" )
// The relationship handles the rest naturally
```

## 6. The "All-in-One" Swiss Army Knife Measure

One measure that changes logic based on 5 slicers using `IF`.

**Why it's bad**: 
- Single thread performance bottleneck.
- Impossible to maintain.

**Fix**: Calculation Groups or individual specific measures.

## 7. Using `CALCULATE` (Obviously)

The No CALCULATE methodology exists specifically to avoid CALCULATE's implicit behavior. For the detailed explanation of why CALCULATE is problematic (black box behavior, debugging difficulty, filter collision, context complexity), see [Philosophy: Why Avoid CALCULATE](./philosophy.md#why-avoid-calculate).

**Fix**: Use the standard Variable Pattern + `FILTER` + `X-Aggregators`. See [Core Pattern](./core-pattern.md).
