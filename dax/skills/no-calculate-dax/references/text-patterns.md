# Text Patterns

Common text manipulation patterns using the No CALCULATE approach.

---

## Text Extraction

Extract a value from a delimited string (e.g., "Name: Brian, Color: Red"):

```dax
Extracted Name = 
    VAR __Find = "Name: "
    VAR __Text = MAX( 'Table'[Column1] )
    VAR __Pos = SEARCH( __Find, __Text, 1, BLANK() )
    VAR __CommaPos = IF( __Pos = BLANK(), BLANK(), 
        SEARCH( ",", __Text, __Pos, LEN( __Text ) + 1 ) 
    )
    VAR __Result = IF( __Pos = BLANK(), BLANK(),
        MID( __Text, __Pos + LEN( __Find ), __CommaPos - __Pos - LEN( __Find ) )
    )
    RETURN __Result
```

---

## Simple Greeting

Time-based personalized greeting using the current user:

```dax
Greeting = 
    VAR __User = USERPRINCIPALNAME()
    VAR __Hour = HOUR( NOW() )
    VAR __Greeting = SWITCH(
        TRUE(),
        __Hour < 12, "Good morning",
        __Hour < 17, "Good afternoon",
        "Good evening"
    )
    RETURN __Greeting & ", " & __User & "!"
```

With friendly name lookup:

```dax
Greeting Friendly = 
    VAR __User = USERPRINCIPALNAME()
    VAR __Name = MAXX( 
        FILTER( 'Users', [UserPrincipalName] = __User ), 
        [FriendlyName] 
    )
    VAR __DisplayName = IF( ISBLANK( __Name ), __User, __Name )
    VAR __Hour = HOUR( NOW() )
    VAR __Greeting = SWITCH(
        TRUE(),
        __Hour < 12, "Good morning",
        __Hour < 17, "Good afternoon",
        "Good evening"
    )
    RETURN __Greeting & ", " & __DisplayName & "!"
```

---

## Anonymize Text

Scramble text for demo/presentation purposes using Unicode offset:

```dax
Anonymized = 
    VAR __Text = MAX( 'Table'[Name] )
    VAR __Length = LEN( __Text )
    VAR __Table = ADDCOLUMNS(
        GENERATESERIES( 1, __Length, 1 ),
        "__Char", MID( __Text, [Value], 1 ),
        "__Code", UNICODE( MID( __Text, [Value], 1 ) )
    )
    VAR __Scrambled = ADDCOLUMNS(
        __Table,
        "__NewChar", 
        VAR __Code = [__Code]
        RETURN SWITCH(
            TRUE(),
            __Code >= 65 && __Code <= 90,   // A-Z
                UNICHAR( MOD( __Code - 65 + 13, 26 ) + 65 ),
            __Code >= 97 && __Code <= 122,  // a-z
                UNICHAR( MOD( __Code - 97 + 13, 26 ) + 97 ),
            [__Char]  // Keep non-letters unchanged
        )
    )
    VAR __Result = CONCATENATEX( __Scrambled, [__NewChar], "", [Value] )
    RETURN __Result
```

> This is a ROT13 cipher - applying it twice restores the original text.

---

## Replace From Right

Replace the Nth occurrence of text counting from the end (not beginning):

```dax
Replace From Right = 
    VAR __Text = MAX( 'Table'[Column1] )
    VAR __Replace = "o"
    VAR __Replacement = "O"
    VAR __Instance = 3  // 3rd from the right
    
    VAR __Instances = DIVIDE( 
        LEN( __Text ) - LEN( SUBSTITUTE( __Text, __Replace, "" ) ), 
        LEN( __Replace ) 
    )
    VAR __Result = IF( 
        __Instance > __Instances, 
        __Text, 
        SUBSTITUTE( __Text, __Replace, __Replacement, __Instances - __Instance + 1 ) 
    )
    RETURN __Result
```

---

## Counting Occurrences

Count how many times a character or word appears in text:

```dax
Count of Word = 
    VAR __Replace = "the"
    VAR __ReplaceLen = LEN( __Replace )
    VAR __Text = MAX( 'Table'[Column1] )
    VAR __Len = LEN( __Text )
    VAR __Substitute = SUBSTITUTE( LOWER( __Text ), __Replace, "" )
    VAR __NewLen = LEN( __Substitute )
    VAR __Result = DIVIDE( __Len - __NewLen, __ReplaceLen )
    RETURN __Result
```

**Counting words** (items separated by spaces):
```dax
Count of Words = 
    VAR __Text = MAX( 'Table'[Column1] )
    VAR __Len = LEN( __Text )
    VAR __NoSpaces = SUBSTITUTE( __Text, " ", "" )
    VAR __Result = __Len - LEN( __NoSpaces ) + 1
    RETURN __Result
```

---

## Text to Table

Convert a delimited string into a table for iteration:

```dax
Text to Table = 
    VAR __Text = "Red|Blue|Green"
    VAR __Path = SUBSTITUTE( __Text, "|", "|" )  // Replace delimiter if needed (e.g., "," to "|")
    VAR __Length = PATHLENGTH( __Path )
    VAR __Table = ADDCOLUMNS(
        GENERATESERIES( 1, __Length, 1 ),
        "Item", PATHITEM( __Path, [Value] )
    )
    RETURN __Table
```

For space-delimited text:
```dax
Words Table = 
    VAR __Text = "The quick brown fox"
    VAR __Path = SUBSTITUTE( __Text, " ", "|" )
    VAR __Length = PATHLENGTH( __Path )
    VAR __Table = ADDCOLUMNS(
        GENERATESERIES( 1, __Length, 1 ),
        "Word", PATHITEM( __Path, [Value] )
    )
    RETURN __Table
```

---

## Dynamic Text for Card Visuals

Show selected filter values in a Card:

```dax
Selected Categories = 
    VAR __Table = FILTER( 'Products', [Category] <> BLANK() )
    VAR __Count = COUNTROWS( __Table )
    VAR __First = MINX( __Table, [Category] )
    VAR __Result = SWITCH( 
        __Count,
        0, "None",
        1, __First,
        __First & " +" & ( __Count - 1 ) & " more"
    )
    RETURN __Result
```

Full list version:
```dax
All Selected = 
    VAR __Table = FILTER( 'Products', [Category] <> BLANK() )
    VAR __Result = IF( 
        COUNTROWS( __Table ) = 0, 
        "None", 
        CONCATENATEX( __Table, [Category], ", ", [Category] ) 
    )
    RETURN __Result
```

---

## Case Functions

```dax
// Convert to lowercase
Lower Text = LOWER( MAX( 'Table'[Text] ) )

// Convert to uppercase
Upper Text = UPPER( MAX( 'Table'[Text] ) )

See [Case Preservation](#case-preservation) for the full pattern.
```

---

## Conditional Formatting Colors

> **Moved**: Conditional formatting patterns have been moved to [Formatting Patterns](./formatting-patterns.md#conditional-formatting-with-measures).

---

## Core Text Functions Reference

| Function | Purpose | Example |
|----------|---------|---------|
| `LEFT(text, n)` | First n characters | `LEFT("Hello", 2)` → "He" |
| `RIGHT(text, n)` | Last n characters | `RIGHT("Hello", 2)` → "lo" |
| `MID(text, start, n)` | n characters from position | `MID("Hello", 2, 3)` → "ell" |
| `LEN(text)` | Character count | `LEN("Hello")` → 5 |
| `SEARCH(find, text)` | Position (case insensitive) | Returns position or error |
| `FIND(find, text)` | Position (case sensitive) | Returns position or error |
| `SUBSTITUTE(text, old, new)` | Replace all occurrences | `SUBSTITUTE("aa", "a", "b")` → "bb" |
| `REPLACE(text, start, n, new)` | Replace by position | `REPLACE("123", 1, 1, "A")` → "A23" |
| `CONCATENATEX(table, expr, sep)` | Join table values | Comma-separated list |

---

## FORMAT String Quick Reference

> **See**: [Format Reference](./format-reference.md) for the complete guide to standard and custom format strings.

---

## Phone Number Validation

Check if a string contains only valid phone characters:

```dax
Is Valid Phone = 
    VAR __Phone = MAX( 'Contacts'[Phone] )
    VAR __ValidChars = "0123456789-+() "
    VAR __CleanPhone = SUBSTITUTE( 
        SUBSTITUTE( 
            SUBSTITUTE( 
                SUBSTITUTE( 
                    SUBSTITUTE( __Phone, " ", "" ), 
                    "-", "" ), 
                "(", "" ), 
            ")", "" ), 
        "+", "" )
    
    // Check if all remaining are digits
    VAR __IsValid = NOT( ISERROR( VALUE( __CleanPhone ) ) )
    VAR __HasDigits = LEN( __CleanPhone ) >= 7
    
    RETURN __IsValid && __HasDigits
```

Format phone number:
```dax
Formatted Phone = 
    VAR __Raw = MAX( 'Contacts'[Phone] )
    VAR __Digits = SUBSTITUTE( 
        SUBSTITUTE( 
            SUBSTITUTE( 
                SUBSTITUTE( __Raw, "-", "" ), 
                " ", "" ), 
            "(", "" ), 
        ")", "" )
    VAR __Len = LEN( __Digits )
    VAR __Result = IF(
        __Len = 10,
        "(" & LEFT( __Digits, 3 ) & ") " & 
        MID( __Digits, 4, 3 ) & "-" & 
        RIGHT( __Digits, 4 ),
        __Raw
    )
    RETURN __Result
```

---

## Case Preservation

DAX is generally case-insensitive (e.g., "ABC" = "abc"). In certain visuals or calculated tables, you may need to preserve case or distinguish between them.

### The Problem
Calculated tables often collapse strings that differ only by case into a single row.

### The Solution: Zero-Width Space
Add `UNICHAR(8203)` (Zero-Width Space) after capital letters or as a suffix to make them distinct to the collation engine while remaining invisible to the user.

```dax
Case Preserved = 
    VAR __Text = [Original Text]
    VAR __Marker = UNICHAR( 8203 )
    RETURN SUBSTITUTE( __Text, "A", "A" & __Marker )
```

> [!TIP]
> This is a hack for calculated tables. In most visual measures, DAX handles case as defined by the data source's collation.

---

## Pangram Checker

Check if text contains every letter of the alphabet:

```dax
Is Pangram = 
    VAR __Text = LOWER( MAX( 'Table'[Sentence] ) )
    VAR __Alphabet = "abcdefghijklmnopqrstuvwxyz"
    VAR __Letters = GENERATESERIES( 1, 26, 1 )
    VAR __Table = ADDCOLUMNS(
        __Letters,
        "__Letter", MID( __Alphabet, [Value], 1 ),
        "__Found", CONTAINSSTRING( __Text, MID( __Alphabet, [Value], 1 ) )
    )
    VAR __MissingCount = COUNTROWS( FILTER( __Table, NOT( [__Found] ) ) )
    RETURN __MissingCount = 0
```

---

## Fuzzy Matching

Techniques to identify and compare text strings that are approximately but not exactly the same.

### Jaccard Similarity

Measures similarity between two sets of characters.

```dax
Jaccard Similarity = 
    VAR __FuzzyThreshold = 0.2
    VAR __MatchWord = MAX( 'Clients'[Client Name] )
    VAR __MatchTable = ADDCOLUMNS( 
        GENERATESERIES( 1, LEN( __MatchWord ), 1 ), 
        "__Char", MID( __MatchWord, [Value], 1 ) 
    )
    VAR __Table = ADDCOLUMNS( 
        DISTINCT( 'Projects'[Project] ), 
        "__JS", 
        VAR __SearchWord = [Project]
        VAR __SearchTable = ADDCOLUMNS( 
            GENERATESERIES( 1, LEN( __SearchWord ), 1 ), 
            "__Char", MID( __SearchWord, [Value], 1 ) 
        )
        VAR __Intersect = COUNTROWS( INTERSECT( __SearchTable, __MatchTable ) )
        VAR __Union = COUNTROWS( UNION( __SearchTable, __MatchTable ) )
        VAR __Result = DIVIDE( __Intersect, __Union, 0 )
        RETURN __Result
    )
    VAR __Max = MAXX( __Table, [__JS] )
    VAR __Result = IF( 
        __Max >= __FuzzyThreshold, 
        MAXX( FILTER( __Table, [__JS] = __Max ), [Project] ), 
        BLANK() 
    )
    RETURN __Result
```

### Levenshtein Distance

Computes the number of insertions, deletions, or substitutions required to transform one string into another.

```dax
Levenshtein Distance = 
    VAR __FuzzyThreshold = 8
    VAR __MatchWord = MAX( 'Clients'[Client Name] )
    VAR __MatchTable = ADDCOLUMNS( 
        GENERATESERIES( 1, LEN( __MatchWord ), 1 ), 
        "__Char", MID( __MatchWord, [Value], 1 ) 
    )
    VAR __Table = ADDCOLUMNS( 
        DISTINCT( 'Projects'[Project] ), 
        "__JS", 
        VAR __SearchWord = [Project]
        VAR __SearchTable = ADDCOLUMNS( 
            GENERATESERIES( 1, LEN( __SearchWord ), 1 ), 
            "__Char", MID( __SearchWord, [Value], 1 ) 
        )
        VAR __Result = IF( 
            COUNTROWS( __SearchTable ) > COUNTROWS( __MatchTable ), 
            COUNTROWS( EXCEPT( __SearchTable, __MatchTable ) ), 
            COUNTROWS( EXCEPT( __MatchTable, __SearchTable ) ) 
        )
        RETURN __Result
    )
    VAR __Min = MINX( __Table, [__JS] )
    VAR __Result = IF( 
        __Min <= __FuzzyThreshold, 
        MAXX( FILTER( __Table, [__JS] = __Min ), [Project] ), 
        BLANK() 
    )
    RETURN __Result
```

### Custom Fuzzy Measure

A specialized algorithm from *DAX for Humans* with custom thresholds and text cleaning:

```dax
Fuzzy Match = 
    VAR __MatchWord = MAX( 'Clients'[Client Name] )
    VAR __CleanMatchThreshold = 4
    VAR __KillThreshold = 3
    VAR __FuzzyThreshold1 = .4
    VAR __FuzzyThreshold2 = .8
    VAR __WordSearchTable = GENERATE( 
        'Projects', 
        VAR __Word = [Project] 
        VAR __Result = ADDCOLUMNS( 
            GENERATESERIES( 3, LEN( __Word ), 1 ), 
            "Search", LEFT( __Word, [Value] ), 
            "Original", __Word 
        ) 
        RETURN __Result 
    )
    VAR __Table = FILTER( 
        ADDCOLUMNS( 
            __WordSearchTable, 
            "Match", SEARCH( [Search], __MatchWord, , BLANK() ) 
        ), 
        NOT( ISBLANK( [Match] ) ) 
    )
    VAR __Max = MAXX( __Table, [Value] )
    VAR __Match = MAXX( FILTER( __Table, [Value] = __Max ), [Search] )
    VAR __Proposed = IF( 
        LEN( __Match ) <= __CleanMatchThreshold, 
        SWITCH( TRUE(), 
            COUNTROWS( FILTER( __Table, [Value] = __Max ) ) > 1, "No Match 1", 
            LEN( __Match ) <= __KillThreshold, "No Match 2", 
            LEN( __Match ) = LEN( __MatchWord ), __Match, 
            LEN( __Match ) / LEN( __MatchWord ) > __FuzzyThreshold1 && SEARCH( __Match, __MatchWord, , 0 ) = 1, __Match, 
            LEN( __Match ) / LEN( __MatchWord ) > __FuzzyThreshold2, __Match, 
            "No Match 3" 
        ), 
        SWITCH( TRUE(), 
            __Match = "Blue Cross" || __Match = "Blue Cross ", __Match, 
            LEN( __Match ) / LEN( __MatchWord ) < __FuzzyThreshold2 && SEARCH( __Match, __MatchWord, , 0 ) <> 1, "No Match 4", 
            __Match 
        ) 
    )
    VAR __Clean1 = IF( RIGHT( __Proposed, 1 ) = "(", LEFT( __Proposed, LEN( __Proposed ) - 1 ), __Proposed )
    VAR __Result = IF( RIGHT( __Clean1, 1 ) = " ", LEFT( __Clean1, LEN( __Clean1 ) - 1 ), __Clean1 )
    RETURN __Result
```

---

## Visual Formatting & SVG

> **Full Patterns**: Visual formatting and SVG patterns have been moved to [Formatting Patterns](./formatting-patterns.md).

