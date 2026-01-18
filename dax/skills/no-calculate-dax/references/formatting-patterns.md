# Formatting Patterns

Visual formatting, conditional formatting, SVG generation, and dynamic text for enhanced Power BI reports.

---

## Conditional Formatting with Measures

Power BI's conditional formatting can use measures to determine colors, icons, and styles.

### Basic Color Scale

```dax
-- For background color (returns hex code)
Color by Value =
    VAR __Value = [Sales]
    VAR __Result = SWITCH(
        TRUE(),
        __Value > 10000, "#2E7D32",  -- Dark green
        __Value > 5000, "#66BB6A",   -- Light green
        __Value > 1000, "#FFF9C4",   -- Yellow
        "#EF5350"                     -- Red
    )
    RETURN __Result
```

**Apply in visual:**
1. Select visual → Format → Conditional formatting
2. Background color → fx (conditional formatting)
3. Format by: Field value
4. Based on field: [Color by Value]

---

### Traffic Light Colors

```dax
Traffic Light =
    VAR __Variance = [Actual] - [Target]
    VAR __PctVariance = DIVIDE( __Variance, [Target], 0 )
    VAR __Result = SWITCH(
        TRUE(),
        __PctVariance >= 0.1, "#00C853",   -- Green: 10%+ above target
        __PctVariance >= 0, "#FFC107",     -- Yellow: Met target
        __PctVariance >= -0.1, "#FF9800",  -- Orange: <10% below
        "#F44336"                          -- Red: 10%+ below target
    )
    RETURN __Result
```

---

### Gradient Color Function

Create smooth color gradients:

```dax
Gradient Color =
    VAR __Value = [Sales]
    VAR __Min = MINX( ALL( 'Sales' ), [Sales] )
    VAR __Max = MAXX( ALL( 'Sales' ), [Sales] )
    VAR __Normalized = DIVIDE( __Value - __Min, __Max - __Min, 0 )

    -- RGB interpolation: Red (255,0,0) to Green (0,255,0)
    VAR __Red = INT( 255 * ( 1 - __Normalized ) )
    VAR __Green = INT( 255 * __Normalized )
    VAR __Blue = 0

    VAR __Hex = "#" &
        RIGHT( "0" & FORMAT( __Red, "X" ), 2 ) &
        RIGHT( "0" & FORMAT( __Green, "X" ), 2 ) &
        RIGHT( "0" & FORMAT( __Blue, "X" ), 2 )

    RETURN __Hex
```

---

### Conditional Icons (Unicode)

Return symbols based on conditions:

```dax
Status Icon =
    VAR __Variance = [Actual vs Target %]
    VAR __Result = SWITCH(
        TRUE(),
        __Variance > 0.1, "🟢 ↑",   -- Up 10%+
        __Variance > 0, "🟡 →",     -- Flat
        __Variance > -0.1, "🟠 ↓",  -- Down <10%
        "🔴 ↓↓"                      -- Down 10%+
    )
    RETURN __Result
```

**Useful Unicode Symbols:**
- Arrows: ↑ ↓ → ← ↗ ↘
- Status: ✓ ✗ ⚠ ⓘ
- Shapes: ● ■ ◆ ★ ○ □
- Trends: ↗ ↘ → 📈 📉
- Misc: 🟢 🟡 🔴 ⚡ 🔥

---

### Data Bars (Text-Based)

Create horizontal bar charts using Unicode:

```dax
Data Bar =
    VAR __Value = [Sales]
    VAR __Max = MAXX( ALL( 'Sales' ), [Sales] )
    VAR __Normalized = DIVIDE( __Value, __Max, 0 )
    VAR __BarLength = INT( __Normalized * 20 )  -- 20 character max width

    VAR __Bar = REPT( "█", __BarLength )
    VAR __Empty = REPT( "░", 20 - __BarLength )

    RETURN __Bar & __Empty & " " & FORMAT( __Value, "#,##0" )
```

---

## SVG Generation

Create inline SVG graphics in measures for rich visualizations.

### Basic SVG Structure

```dax
SVG Template =
    "<svg width='100' height='20' xmlns='http://www.w3.org/2000/svg'>" &
    "  <!-- SVG content here -->" &
    "</svg>"
```

---

### Sparkline SVG

Compact trend visualization:

```dax
Sparkline =
    VAR __Data = ADDCOLUMNS(
        SUMMARIZE( 'Sales', 'Calendar'[Date] ),
        "__Value", [Sales]
    )
    VAR __Points = CONCATENATEX(
        __Data,
        VAR __X = DATEDIFF( MIN( 'Calendar'[Date] ), [Date], DAY ) * 2
        VAR __Y = 50 - ( [__Value] / MAXX( __Data, [__Value] ) * 40 )
        RETURN __X & "," & __Y,
        " ",
        [Date], ASC
    )
    VAR __SVG =
        "<svg width='200' height='50' xmlns='http://www.w3.org/2000/svg'>" &
        "  <polyline points='" & __Points & "' " &
        "    fill='none' stroke='#2196F3' stroke-width='2'/>" &
        "</svg>"
    RETURN __SVG
```

---

### Progress Bar SVG

Visual progress indicator:

```dax
Progress Bar =
    VAR __Actual = [Actual]
    VAR __Target = [Target]
    VAR __Pct = DIVIDE( __Actual, __Target, 0 )
    VAR __Width = INT( __Pct * 100 )

    VAR __Color = SWITCH(
        TRUE(),
        __Pct >= 1, "#4CAF50",      -- Green: Complete
        __Pct >= 0.75, "#8BC34A",   -- Light green
        __Pct >= 0.5, "#FFC107",    -- Yellow
        __Pct >= 0.25, "#FF9800",   -- Orange
        "#F44336"                    -- Red
    )

    VAR __SVG =
        "<svg width='100' height='20' xmlns='http://www.w3.org/2000/svg'>" &
        "  <rect width='100' height='20' fill='#E0E0E0' rx='4'/>" &
        "  <rect width='" & __Width & "' height='20' fill='" & __Color & "' rx='4'/>" &
        "  <text x='50' y='14' text-anchor='middle' font-size='11' fill='#000'>" &
            FORMAT( __Pct, "0%") &
        "  </text>" &
        "</svg>"
    RETURN __SVG
```

---

### Gauge SVG

Semi-circular gauge:

```dax
Gauge =
    VAR __Value = [Sales]
    VAR __Max = [Target]
    VAR __Pct = DIVIDE( __Value, __Max, 0 )
    VAR __Angle = -90 + ( __Pct * 180 )  -- -90° to 90° (bottom to bottom)

    VAR __X = 50 + 40 * COS( RADIANS( __Angle ) )
    VAR __Y = 50 + 40 * SIN( RADIANS( __Angle ) )

    VAR __Color = SWITCH(
        TRUE(),
        __Pct >= 0.9, "#4CAF50",
        __Pct >= 0.7, "#8BC34A",
        __Pct >= 0.5, "#FFC107",
        "#F44336"
    )

    VAR __SVG =
        "<svg width='100' height='60' xmlns='http://www.w3.org/2000/svg'>" &
        "  <!-- Gauge arc -->" &
        "  <path d='M 10,50 A 40,40 0 0,1 90,50' " &
        "    fill='none' stroke='#E0E0E0' stroke-width='8'/>" &
        "  <!-- Value arc -->" &
        "  <path d='M 10,50 A 40,40 0 " &
            IF( __Pct > 0.5, "1,1", "0,1" ) & " " & __X & "," & __Y & "' " &
        "    fill='none' stroke='" & __Color & "' stroke-width='8'/>" &
        "  <!-- Center text -->" &
        "  <text x='50' y='45' text-anchor='middle' font-size='14' font-weight='bold'>" &
            FORMAT( __Pct, "0%" ) &
        "  </text>" &
        "</svg>"
    RETURN __SVG
```

---

### Bullet Chart SVG

Compact KPI visualization:

```dax
Bullet Chart =
    VAR __Actual = [Actual]
    VAR __Target = [Target]
    VAR __Max = __Target * 1.2

    VAR __ActualWidth = DIVIDE( __Actual, __Max, 0 ) * 200
    VAR __TargetX = DIVIDE( __Target, __Max, 0 ) * 200

    VAR __SVG =
        "<svg width='220' height='30' xmlns='http://www.w3.org/2000/svg'>" &
        "  <!-- Background ranges -->" &
        "  <rect x='0' y='5' width='200' height='20' fill='#E8F5E9'/>" &
        "  <rect x='0' y='5' width='" & (__TargetX * 0.6) & "' height='20' fill='#C8E6C9'/>" &
        "  <rect x='0' y='5' width='" & (__TargetX * 0.3) & "' height='20' fill='#A5D6A7'/>" &
        "  <!-- Actual bar -->" &
        "  <rect x='0' y='10' width='" & __ActualWidth & "' height='10' fill='#1976D2'/>" &
        "  <!-- Target marker -->" &
        "  <line x1='" & __TargetX & "' y1='5' x2='" & __TargetX & "' y2='25' " &
        "    stroke='#D32F2F' stroke-width='3'/>" &
        "</svg>"
    RETURN __SVG
```

---

### Trend Arrow SVG

Visual trend indicator:

```dax
Trend Arrow =
    VAR __Current = [Sales]
    VAR __Previous = [Sales PY]
    VAR __Change = DIVIDE( __Current - __Previous, __Previous, 0 )

    VAR __Angle = SWITCH(
        TRUE(),
        __Change > 0.1, -45,      -- Up arrow
        __Change > 0, -20,        -- Slight up
        __Change > -0.1, 0,       -- Flat
        __Change > -0.2, 20,      -- Slight down
        45                         -- Down arrow
    )

    VAR __Color = SWITCH(
        TRUE(),
        __Change > 0.1, "#4CAF50",
        __Change > 0, "#8BC34A",
        __Change > -0.1, "#FFC107",
        "#F44336"
    )

    VAR __SVG =
        "<svg width='40' height='40' xmlns='http://www.w3.org/2000/svg'>" &
        "  <g transform='rotate(" & __Angle & " 20 20)'>" &
        "    <line x1='20' y1='30' x2='20' y2='10' stroke='" & __Color & "' stroke-width='3'/>" &
        "    <polygon points='20,5 15,12 25,12' fill='" & __Color & "'/>" &
        "  </g>" &
        "</svg>"
    RETURN __SVG
```

---

### Star Rating SVG

Display ratings visually:

```dax
Star Rating =
    VAR __Rating = [Avg Rating]  -- 0 to 5
    VAR __FullStars = INT( __Rating )
    VAR __HalfStar = IF( __Rating - __FullStars >= 0.5, 1, 0 )

    VAR __StarSVG = "★"
    VAR __EmptyStar = "☆"

    VAR __Result =
        REPT( __StarSVG, __FullStars ) &
        IF( __HalfStar = 1, "⯨", "" ) &
        REPT( __EmptyStar, 5 - __FullStars - __HalfStar )

    RETURN __Result
```

---

## Dynamic Text Formatting

### Conditional Number Formatting

```dax
Formatted Sales =
    VAR __Value = [Sales]
    VAR __Result = SWITCH(
        TRUE(),
        __Value >= 1000000, FORMAT( __Value / 1000000, "$0.0") & "M",
        __Value >= 1000, FORMAT( __Value / 1000, "$0.0" ) & "K",
        FORMAT( __Value, "$0" )
    )
    RETURN __Result
```

---

### Variance Text with Color

```dax
Variance Display =
    VAR __Actual = [Actual]
    VAR __Target = [Target]
    VAR __Variance = __Actual - __Target
    VAR __PctVariance = DIVIDE( __Variance, __Target, 0 )

    VAR __Arrow = IF( __Variance > 0, "↑", "↓" )
    VAR __Color = IF( __Variance > 0, "#4CAF50", "#F44336" )

    VAR __Text =
        "<span style='color:" & __Color & ";font-weight:bold'>" &
        __Arrow & " " & FORMAT( ABS( __Variance ), "#,##0" ) &
        " (" & FORMAT( ABS( __PctVariance ), "0.0%" ) & ")" &
        "</span>"

    RETURN __Text
```

---

### Dynamic Label with Icon

```dax
Sales Label =
    VAR __Value = [Sales]
    VAR __PY = [Sales PY]
    VAR __Change = __Value - __PY

    VAR __Icon = SWITCH(
        TRUE(),
        __Change > 0, "🟢",
        __Change = 0, "🟡",
        "🔴"
    )

    VAR __Result = __Icon & " " & FORMAT( __Value, "$#,##0" )
    RETURN __Result
```

---

## Conditional Formatting by Rules

### Cell Highlighting

```dax
-- For table cell background
Cell Background =
    VAR __Value = [Sales]
    VAR __Threshold = [Target]
    RETURN IF( __Value < __Threshold, "#FFCDD2", "#C8E6C9" )
```

### Font Color

```dax
Font Color =
    VAR __Variance = [Actual vs Target %]
    RETURN SWITCH(
        TRUE(),
        __Variance >= 0.1, "#1B5E20",   -- Dark green
        __Variance >= 0, "#33691E",     -- Olive
        __Variance >= -0.1, "#E65100",  -- Orange
        "#B71C1C"                        -- Dark red
    )
```

### Data Bar Color

```dax
Data Bar Color =
    VAR __Value = [Sales]
    VAR __Avg = AVERAGEX( ALL( 'Sales' ), [Sales] )
    RETURN IF( __Value > __Avg, "#2196F3", "#90CAF9" )
```

---

## KPI Card Formatting

### Complete KPI Card

```dax
KPI Card =
    VAR __Value = [Sales]
    VAR __Target = [Target]
    VAR __PY = [Sales PY]

    VAR __vsTarget = DIVIDE( __Value - __Target, __Target, 0 )
    VAR __vsPY = DIVIDE( __Value - __PY, __PY, 0 )

    VAR __TargetIcon = IF( __vsTarget >= 0, "✓", "✗" )
    VAR __TrendIcon = IF( __vsPY >= 0, "↑", "↓" )

    VAR __Result =
        "💰 Sales: " & FORMAT( __Value, "$#,##0" ) & UNICHAR(10) &
        __TargetIcon & " vs Target: " & FORMAT( __vsTarget, "+0.0%;-0.0%" ) & UNICHAR(10) &
        __TrendIcon & " vs PY: " & FORMAT( __vsPY, "+0.0%;-0.0%" )

    RETURN __Result
```

---

## Heat Map Formatting

### Intensity-Based Color

```dax
Heat Map Color =
    VAR __Value = [Sales]
    VAR __Min = MINX( ALLSELECTED( 'Sales' ), [Sales] )
    VAR __Max = MAXX( ALLSELECTED( 'Sales' ), [Sales] )
    VAR __Normalized = DIVIDE( __Value - __Min, __Max - __Min, 0 )

    -- Gradient from white to dark blue
    VAR __Intensity = INT( 255 * ( 1 - __Normalized ) )

    VAR __Hex = "#" &
        RIGHT( "0" & FORMAT( __Intensity, "X" ), 2 ) &
        RIGHT( "0" & FORMAT( __Intensity, "X" ), 2 ) &
        "FF"

    RETURN __Hex
```

---

## Tooltip Formatting

### Rich Tooltip Content

```dax
Tooltip Text =
    VAR __Category = MAX( 'Product'[Category] )
    VAR __Sales = [Sales]
    VAR __Quantity = [Quantity]
    VAR __AvgPrice = DIVIDE( __Sales, __Quantity, 0 )

    VAR __Result =
        "Category: " & __Category & UNICHAR(10) &
        "━━━━━━━━━━━━━━━" & UNICHAR(10) &
        "💵 Sales: " & FORMAT( __Sales, "$#,##0" ) & UNICHAR(10) &
        "📦 Quantity: " & FORMAT( __Quantity, "#,##0" ) & UNICHAR(10) &
        "💰 Avg Price: " & FORMAT( __AvgPrice, "$#,##0.00" )

    RETURN __Result
```

---

## Accessibility Patterns

### High Contrast Mode

```dax
Accessible Color =
    VAR __Value = [Sales]
    VAR __Target = [Target]

    -- Use patterns instead of colors for accessibility
    RETURN SWITCH(
        TRUE(),
        __Value >= __Target * 1.1, "██████ (Excellent)",
        __Value >= __Target, "████░░ (Good)",
        __Value >= __Target * 0.9, "███░░░ (Fair)",
        "██░░░░ (Poor)"
    )
```

---

## Performance Considerations

### Avoid Complex SVG in Large Visuals

**Bad (slow with 1000+ rows):**
```dax
Sparkline for Every Row = [Complex Sparkline SVG]
```

**Good (summarize first):**
```dax
Category Sparkline =
    VAR __Category = MAX( 'Product'[Category] )
    VAR __Data = FILTER( ALL( 'Sales' ), [Category] = __Category )
    -- Then generate SVG from __Data
```

### Cache Formatting Measures

Reuse formatting logic:

```dax
-- Base formatting function
_Color by Threshold =
    VAR __Value = [Sales]
    VAR __Threshold = 5000
    RETURN IF( __Value > __Threshold, "#4CAF50", "#F44336" )

-- Use in multiple places
Background Color = [_Color by Threshold]
Font Color = [_Color by Threshold]
```

---

## Common Formatting Patterns

| Need | Pattern |
|------|---------|
| Traffic lights | Switch TRUE with 3-5 color tiers |
| Progress bar | SVG rect with dynamic width |
| Sparkline | SVG polyline with CONCATENATEX |
| Status icons | Unicode symbols (🟢 🟡 🔴) |
| Trend arrows | Unicode arrows (↑ ↓ →) |
| Data bars | REPT("█", n) for text bars |
| Color gradient | RGB interpolation to hex |
| KPI cards | UNICHAR(10) for line breaks |

---

## See Also

- [Text Patterns](text-patterns.md) - Text manipulation functions
- [Number Patterns](number-patterns.md) - FORMAT() reference
- [Format Reference](format-reference.md) - Complete FORMAT() syntax guide
