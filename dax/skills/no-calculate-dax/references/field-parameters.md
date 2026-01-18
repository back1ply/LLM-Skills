# Field Parameters

Field Parameters allow users to dynamically change the dimensions or measures being analyzed in a visual. They replace the older "Disconnected Table + SWITCH" pattern.

---

## Dynamic Dimension (Axis)

Allow a user to toggle a chart between "By Region", "By Product", or "By Customer".

### Setup
1.  **Modeling Tab** > **New Parameter** > **Fields**.
2.  Select columns: `Region[Region]`, `Product[Category]`, `Customer[Name]`.
3.  Name it `Dynamic Dimension`.

### DAX Generated (Behind the Scenes)
Power BI automatically generates a calculated table:

```dax
Dynamic Dimension = {
    ("Region", NAMEOF('Region'[Region]), 0),
    ("Category", NAMEOF('Product'[Category]), 1),
    ("Customer", NAMEOF('Customer'[Name]), 2)
}
```

### Usage
*   Add `Dynamic Dimension` column to the **X-axis** or **Rows** of a visual.
*   Add a slicer for `Dynamic Dimension`.

---

## Dynamic Measures

Allow a user to toggle between "Sales", "Profit", and "Margin %".

### Setup
1.  **Modeling Tab** > **New Parameter** > **Fields**.
2.  Select measures: `[Total Sales]`, `[Total Profit]`, `[Margin %]`.
3.  Name it `Dynamic Measure`.

### DAX Generated
```dax
Dynamic Measure = {
    ("Total Sales", NAMEOF('Sales'[Total Sales]), 0),
    ("Total Profit", NAMEOF('Sales'[Total Profit]), 1),
    ("Margin %", NAMEOF('Sales'[Margin %]), 2)
}
```

### Usage
*   Add `Dynamic Measure` to the **Values** or **Y-axis** of a visual.
*   Add a slicer for `Dynamic Measure`.

---

## Advanced: Hybrid "No CALCULATE" Pattern

You can add custom columns to the Field Parameter table to control grouping or sorting, just like any other DAX table.

### Adding a "Report Group" Column
Modify the DAX to add a 4th column for grouping in slicers:

```dax
Dynamic Indicators = {
    ("Revenue", NAMEOF('Sales'[Revenue]), 0, "Financial"),
    ("Cost", NAMEOF('Sales'[Cost]), 1, "Financial"),
    ("Units", NAMEOF('Sales'[Units]), 2, "Operational"),
    ("Orders", NAMEOF('Sales'[Orders]), 3, "Operational")
}
```
*   **Usage**: Create a hierarchy slicer using `[Value4]` (Group) and `[Dynamic Indicators]` (Name).

---

## Retrieving Selected Parameter

Sometimes you need to know *what* parameter is selected to change a title or partial logic.

```dax
Selected Metric Name = 
    SELECTEDVALUE( 'Dynamic Measure'[Dynamic Measure], "Multiple Selected" )
```

---

## Best Practices

*   **NAMEOF**: Always use `NAMEOF()` function. It ensures that if you rename the source measure/column, the parameter updates automatically.
*   **Slicer Sync**: Field Parameters respect slicers just like normal relationships.
*   **Format Strings**: Field Parameters automatically preserve the specific format string of the selected measure (e.g., Currency for Sales, Percentage for Margin).
