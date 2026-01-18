# FORMAT() Function Reference

Complete reference for the DAX FORMAT() function for numbers, dates, and custom formatting.

---

## Syntax

```dax
FORMAT( <value>, <format_string> )
```

Returns a **text string** representation of the value.

**Important:** FORMAT always returns text, not a number. Use for display only.

---

## Number Formatting

### Basic Number Patterns

| Pattern | Example Input | Output | Description |
|---------|---------------|--------|-------------|
| `"0"` | 1234.5 | "1235" | Integer (rounds) |
| `"0.0"` | 1234.567 | "1234.6" | One decimal |
| `"0.00"` | 1234.5 | "1234.50" | Two decimals |
| `"0.000"` | 1234.5 | "1234.500" | Three decimals |
| `"#,##0"` | 1234567 | "1,234,567" | Thousands separator |
| `"#,##0.00"` | 1234.5 | "1,234.50" | Thousands + decimals |

### Currency Formatting

```dax
-- US Dollar
FORMAT( [Sales], "$#,##0.00" )         → "$1,234.50"
FORMAT( [Sales], "$#,##0" )            → "$1,235"

-- Euro
FORMAT( [Sales], "€#,##0.00" )         → "€1,234.50"

-- British Pound
FORMAT( [Sales], "£#,##0.00" )         → "£1,234.50"

-- Yen (no decimals)
FORMAT( [Sales], "¥#,##0" )            → "¥1,235"
```

### Percentage Formatting

```dax
FORMAT( 0.1234, "0%" )                 → "12%"
FORMAT( 0.1234, "0.0%" )               → "12.3%"
FORMAT( 0.1234, "0.00%" )              → "12.34%"
FORMAT( 0.1256, "0.00%" )              → "12.56%"
```

**Note:** FORMAT automatically multiplies by 100 for percentage formats.

### Negative Number Formats

Use `;` to separate positive;negative;zero formats:

```dax
-- Positive; Negative
FORMAT( -100, "$#,##0;($#,##0)" )      → "($100)"

-- Positive; Negative; Zero
FORMAT( 0, "#,##0;(#,##0);Zero" )      → "Zero"

-- With colors (HTML)
FORMAT( -100, "$#,##0;[Red]$#,##0" )   → "-$100" (in red if HTML)
```

### Scientific Notation

```dax
FORMAT( 1234567, "0.00E+00" )          → "1.23E+06"
FORMAT( 0.00012, "0.00E+00" )          → "1.20E-04"
```

### Scaling Formats

Divide by 1000, 1000000:

```dax
-- Thousands (K)
FORMAT( 1234567, "#,##0,K" )           → "1,235K"
FORMAT( 1234567, "#,##0.0,K" )         → "1,234.6K"

-- Millions (M)
FORMAT( 1234567, "#,##0,,M" )          → "1M"
FORMAT( 1234567, "#,##0.0,,M" )        → "1.2M"
FORMAT( 1234567, "#,##0.00,,M" )       → "1.23M"

-- Billions (B)
FORMAT( 1234567890, "#,##0,,,B" )      → "1B"
```

**Pattern:** Each comma represents division by 1,000.

---

## Date Formatting

### Standard Date Formats

| Pattern | Example Output | Description |
|---------|----------------|-------------|
| `"m/d/yyyy"` | "1/15/2024" | US format |
| `"dd/mm/yyyy"` | "15/01/2024" | European format |
| `"yyyy-mm-dd"` | "2024-01-15" | ISO format |
| `"mm-dd-yyyy"` | "01-15-2024" | Dash separated |
| `"mm/dd/yy"` | "01/15/24" | Short year |

### Month Name Formats

```dax
FORMAT( [Date], "mmmm" )               → "January"
FORMAT( [Date], "mmm" )                → "Jan"
FORMAT( [Date], "mm" )                 → "01"
FORMAT( [Date], "m" )                  → "1"
```

### Day Formats

```dax
FORMAT( [Date], "dddd" )               → "Monday"
FORMAT( [Date], "ddd" )                → "Mon"
FORMAT( [Date], "dd" )                 → "15"
FORMAT( [Date], "d" )                  → "15"
```

### Year Formats

```dax
FORMAT( [Date], "yyyy" )               → "2024"
FORMAT( [Date], "yy" )                 → "24"
```

### Combined Date Formats

```dax
FORMAT( [Date], "dddd, mmmm d, yyyy" ) → "Monday, January 15, 2024"
FORMAT( [Date], "ddd mmm d yyyy" )     → "Mon Jan 15 2024"
FORMAT( [Date], "mmmm yyyy" )          → "January 2024"
FORMAT( [Date], "mmm-yy" )             → "Jan-24"
```

### Quarter Formatting

```dax
FORMAT( [Date], "Q" )                  → "1" (quarter number)
"Q" & FORMAT( [Date], "Q" )            → "Q1"
"Q" & FORMAT( [Date], "Q yyyy" )       → "Q1 2024"
```

**Note:** Must combine with text for "Q" prefix.

---

## Time Formatting

### Basic Time Formats

```dax
FORMAT( [Time], "hh:mm:ss" )           → "14:30:45"
FORMAT( [Time], "hh:mm" )              → "14:30"
FORMAT( [Time], "h:mm AM/PM" )         → "2:30 PM"
FORMAT( [Time], "h:mm:ss AM/PM" )      → "2:30:45 PM"
```

### 12 vs 24 Hour

```dax
-- 24-hour
FORMAT( TIME( 14, 30, 0 ), "HH:mm" )   → "14:30"

-- 12-hour
FORMAT( TIME( 14, 30, 0 ), "h:mm AM/PM" ) → "2:30 PM"
```

### Datetime Formats

```dax
FORMAT( [DateTime], "mm/dd/yyyy hh:mm:ss" )
    → "01/15/2024 14:30:45"

FORMAT( [DateTime], "yyyy-mm-dd HH:mm" )
    → "2024-01-15 14:30"

FORMAT( [DateTime], "ddd mmm d, yyyy h:mm AM/PM" )
    → "Mon Jan 15, 2024 2:30 PM"
```

---

## Custom Conditional Formatting
 
For advanced patterns like **Dynamic Format Based on Value** (e.g., auto-switching between K, M, B) or **Conditional Decimal Places**, please refer to the specialized [Formatting Patterns](./formatting-patterns.md#dynamic-text-formatting) guides.

---

## Locale-Specific Formatting

### Using FORMAT with Locale

```dax
-- US English
FORMAT( [Date], "long date", "en-US" )
    → "Monday, January 15, 2024"

-- UK English
FORMAT( [Date], "long date", "en-GB" )
    → "15 January 2024"

-- German
FORMAT( [Date], "long date", "de-DE" )
    → "Montag, 15. Januar 2024"

-- French
FORMAT( [Date], "long date", "fr-FR" )
    → "lundi 15 janvier 2024"
```

### Currency by Locale

```dax
-- US format
FORMAT( 1234.5, "currency", "en-US" )  → "$1,234.50"

-- UK format
FORMAT( 1234.5, "currency", "en-GB" )  → "£1,234.50"

-- Euro (Germany)
FORMAT( 1234.5, "currency", "de-DE" )  → "1.234,50 €"

-- Euro (France)
FORMAT( 1234.5, "currency", "fr-FR" )  → "1 234,50 €"
```

---

## Special Formats

### Leading Zeros

```dax
FORMAT( 42, "00000" )                  → "00042"
FORMAT( 7, "000" )                     → "007"
```

**Use case:** Product codes, invoice numbers

### Fixed Width

```dax
-- Always 10 characters, pad with spaces
FORMAT( [Value], "@@@@@@@@@@@" )       → "  Value   "
```

### Text Format

```dax
FORMAT( [Text], "@" )                  → Returns text as-is
```

---

## Practical Format Patterns

### Invoice Number

```dax
Invoice Number =
    "INV-" & FORMAT( [InvoiceID], "00000" )
    → "INV-00123"
```

### Product Code

```dax
Product Code =
    FORMAT( [CategoryID], "00" ) & "-" &
    FORMAT( [ProductID], "0000" )
    → "03-0042"
```

### Duration (Seconds to HH:MM:SS)

```dax
Duration Format =
    VAR __TotalSeconds = [Duration]
    VAR __Hours = INT( __TotalSeconds / 3600 )
    VAR __Minutes = INT( MOD( __TotalSeconds, 3600 ) / 60 )
    VAR __Seconds = MOD( __TotalSeconds, 60 )
    RETURN
        FORMAT( __Hours, "00" ) & ":" &
        FORMAT( __Minutes, "00" ) & ":" &
        FORMAT( __Seconds, "00" )
```

### File Size

```dax
File Size =
    VAR __Bytes = [Size]
    VAR __Result = SWITCH(
        TRUE(),
        __Bytes >= 1073741824,
            FORMAT( __Bytes / 1073741824, "0.00" ) & " GB",
        __Bytes >= 1048576,
            FORMAT( __Bytes / 1048576, "0.00" ) & " MB",
        __Bytes >= 1024,
            FORMAT( __Bytes / 1024, "0.00" ) & " KB",
        FORMAT( __Bytes, "#,##0" ) & " bytes"
    )
    RETURN __Result
```

---

## Format Pattern Reference

### Number Format Characters

| Character | Meaning |
|-----------|---------|
| `0` | Digit placeholder (shows zero if no digit) |
| `#` | Digit placeholder (nothing if no digit) |
| `.` | Decimal point |
| `,` | Thousands separator or scale divisor |
| `%` | Multiply by 100 and show percent sign |
| `E` | Scientific notation |
| `;` | Section separator (positive;negative;zero) |

### Date/Time Format Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `d` | Day (1 or 2 digits) | 5, 15 |
| `dd` | Day (always 2 digits) | 05, 15 |
| `ddd` | Day name (abbreviated) | Mon |
| `dddd` | Day name (full) | Monday |
| `m` | Month (1 or 2 digits) | 1, 12 |
| `mm` | Month (always 2 digits) | 01, 12 |
| `mmm` | Month name (abbreviated) | Jan |
| `mmmm` | Month name (full) | January |
| `yy` | Year (2 digits) | 24 |
| `yyyy` | Year (4 digits) | 2024 |
| `h` | Hour (1 or 2 digits) | 2, 14 |
| `hh` | Hour (always 2 digits) | 02, 14 |
| `H` | Hour 24-hour (1 or 2 digits) | 2, 14 |
| `HH` | Hour 24-hour (2 digits) | 02, 14 |
| `mm` | Minutes (context-dependent) | 05, 30 |
| `ss` | Seconds | 00, 59 |
| `AM/PM` | 12-hour time indicator | AM, PM |

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Using FORMAT in calculations | Returns text, not number | Use FORMAT only for display |
| `"#,#0"` instead of `"#,##0"` | Won't show thousands separator | Need double `##` |
| `"mm"` for hours | Shows minutes, not hours | Use `"HH"` for 24-hour |
| Forgetting locale for currency | Wrong currency symbol | Specify locale: `"currency", "en-US"` |
| `FORMAT( 0.15, "#%" )` | Shows "15%" not "0.15%" | Use `"0%"` not `"#%"` |

---

## Performance Considerations

1. **FORMAT is text-only:** Cannot perform math on FORMAT results
2. **Use sparingly in tables:** Formatting 1000s of rows is slow
3. **Base + Display pattern:** Create base measure (numeric), display measure (formatted)

```dax
-- Base (numeric, reusable)
Sales = SUMX( 'Sales', [Amount] )

-- Display (formatted, for visuals only)
Sales (formatted) = FORMAT( [Sales], "$#,##0" )
```

---

## Quick Reference Examples

### Numbers

```dax
FORMAT( 1234.567, "0" )                → "1235"
FORMAT( 1234.567, "0.00" )             → "1234.57"
FORMAT( 1234.567, "#,##0.00" )         → "1,234.57"
FORMAT( 1234.567, "$#,##0.00" )        → "$1,234.57"
FORMAT( 1234567, "#,##0,K" )           → "1,235K"
FORMAT( 1234567, "#,##0.0,,M" )        → "1.2M"
FORMAT( 0.567, "0.00%" )               → "56.70%"
```

### Dates

```dax
FORMAT( DATE(2024,1,15), "mm/dd/yyyy" )     → "01/15/2024"
FORMAT( DATE(2024,1,15), "dddd mmmm d" )    → "Monday January 15"
FORMAT( DATE(2024,1,15), "mmm-yy" )         → "Jan-24"
FORMAT( DATE(2024,1,15), "yyyy-mm-dd" )     → "2024-01-15"
```

### Time

```dax
FORMAT( TIME(14,30,45), "hh:mm:ss" )        → "14:30:45"
FORMAT( TIME(14,30,45), "h:mm AM/PM" )      → "2:30 PM"
```

---

## See Also

- [Number Patterns](number-patterns.md) - Number calculations
- [Text Patterns](text-patterns.md) - Text manipulation
- [Formatting Patterns](formatting-patterns.md) - Visual formatting with SVG
