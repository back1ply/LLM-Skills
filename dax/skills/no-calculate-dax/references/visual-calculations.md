# Visual Calculations

Visual calculations allow you to perform calculations directly on the visual's data matrix. This is the ultimate "No CALCULATE" feature because it operates on the result table of the visual, not the source model.

---

## Core Philosophy

1.  **Visual as a Table**: Treat the visual (Matrix/Table) as a materialized table.
2.  **Explicit Direction**: Always specify `ROWS` or `COLUMNS` to avoid ambiguity.
3.  **Performance**: These run *after* the query returns, often faster for things like running totals.

---

## Running Sum

Accumulate values across rows (e.g., Running Total over Date).

```dax
Running Total = RUNNINGSUM( [Sales Amount], ROWS )
```

With Reset (e.g., Restart every Year):
```dax
// Requires [Year] field in the visual
Running Total YTD = RUNNINGSUM( [Sales Amount], HIGHESTPARENT, ROWS )
```

---

## Moving Average

Simple rolling average over the visible axis.

```dax
// 3-Period Moving Average (Current + Previous 2)
Moving Avg 3M = MOVINGAVERAGE( [Sales Amount], 2, ROWS )
```

---

## Previous / Next

Get value from previous row (Lead/Lag logic).

```dax
// Growth vs Previous Row
MoM Growth = 
    VAR __Prev = PREVIOUS( [Sales Amount], ROWS )
    VAR __Curr = [Sales Amount]
    RETURN DIVIDE( __Curr - __Prev, __Prev )
```

---

## Rank in Visual

Rank items based on what is currently displayed.

```dax
// Rank 1 to N based on Sales
Visual Rank = RANK( [Sales Amount], ROWS, ORDERBY( [Sales Amount], DESC ) )
```

---

## Collapse / Expand

Handle hierarchy levels (Matrix visual only).

```dax
// Show different val if collapsed vs expanded
Hierarchy logic = 
    IF( 
        ISATLEVEL( [Product] ), 
        [Sales Amount], 
        [Sales Amount] * 1.1 -- Fake example logic for summary
    )
```

---

## Best Practices

*   **Edit Mode**: You must use the "New visual calculation" button in the ribbon (or right-click measure in visual) to create these. They are stored **in the visual**, not the model.
*   **Hiding Fields**: You can create intermediate visual calcs and hide them from the final view.
*   **Matrix Traversal**: Use `AXIS` parameter carefully in Matrix visuals. `ROWS` goes down, `COLUMNS` goes across.
