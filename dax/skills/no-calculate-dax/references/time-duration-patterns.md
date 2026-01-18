# Time and Duration Patterns

Working with times, durations, and time zone conversions using the No CALCULATE approach.

---

## Time Basics

In DAX, time is stored as a decimal fraction of a day:
- `0.5` = 12:00 PM (noon)
- `0.25` = 6:00 AM
- `1/24` = 1 hour
- `1/24/60` = 1 minute

```dax
// Create a time value
Time Value = TIME( 14, 30, 0 )  // 2:30 PM

// Extract components
Hour = HOUR( [Time] )
Minute = MINUTE( [Time] )
Second = SECOND( [Time] )
```

---

## Time Arithmetic

```dax
// Add 2 hours to a time
Plus 2 Hours = [Time] + 2/24

// Add 30 minutes
Plus 30 Minutes = [Time] + 30/24/60

// Subtract 45 minutes
Minus 45 Minutes = [Time] - 45/24/60

// Difference in hours between two times
Hours Between = ( [EndTime] - [StartTime] ) * 24

// Difference in minutes
Minutes Between = ( [EndTime] - [StartTime] ) * 24 * 60
```

---

## Duration to Decimal Hours

Convert a start/end time to decimal hours:
```dax
Decimal Hours = 
    VAR __Start = MIN( 'Table'[Start Time] )
    VAR __End = MAX( 'Table'[End Time] )
    VAR __Result = ( __End - __Start ) * 24
    RETURN __Result
```

---

## Seconds to Duration String

Convert seconds to a formatted duration (D:H:M:S):
```dax
Seconds to Duration = 
    VAR __Seconds = [Total Seconds]
    VAR __Days = TRUNC( __Seconds / 86400 )
    VAR __Remainder1 = MOD( __Seconds, 86400 )
    VAR __Hours = TRUNC( __Remainder1 / 3600 )
    VAR __Remainder2 = MOD( __Remainder1, 3600 )
    VAR __Minutes = TRUNC( __Remainder2 / 60 )
    VAR __Secs = MOD( __Remainder2, 60 )
    VAR __Result = __Days & ":" & __Hours & ":" & __Minutes & ":" & __Secs
    RETURN __Result
```

---

## Duration String to Seconds

Convert "HH:MM:SS" format to total seconds:
```dax
Duration to Seconds = 
    VAR __Text = [Duration String]
    VAR __Path = SUBSTITUTE( __Text, ":", "|" )
    VAR __Hours = VALUE( PATHITEM( __Path, 1 ) )
    VAR __Minutes = VALUE( PATHITEM( __Path, 2 ) )
    VAR __Seconds = VALUE( PATHITEM( __Path, 3 ) )
    VAR __Result = __Hours * 3600 + __Minutes * 60 + __Seconds
    RETURN __Result
```

---

## Milliseconds to Duration

```dax
Milliseconds to Duration = 
    VAR __Ms = [Milliseconds]
    VAR __Days = TRUNC( __Ms / 86400000 )
    VAR __R1 = MOD( __Ms, 86400000 )
    VAR __Hours = TRUNC( __R1 / 3600000 )
    VAR __R2 = MOD( __R1, 3600000 )
    VAR __Mins = TRUNC( __R2 / 60000 )
    VAR __R3 = MOD( __R2, 60000 )
    VAR __Secs = TRUNC( __R3 / 1000 )
    VAR __Millis = MOD( __R3, 1000 )
    VAR __Result = __Days & ":" & __Hours & ":" & __Mins & ":" & __Secs & ":" & __Millis
    RETURN __Result
```

---

## Formatting Durations

### Decimal Days to Duration String

Convert decimal days (e.g., `1.5`) to `DD:HH:MM:SS`:

```dax
Duration String =
    VAR __Val = [DecimalDuration]
    VAR __D = TRUNC( __Val )
    VAR __H = TRUNC( ( __Val - __D ) * 24 )
    VAR __M = TRUNC( ( __Val - __D - __H/24 ) * 24 * 60 )
    VAR __S = TRUNC( ( __Val - __D - __H/24 - __M/24/60 ) * 24 * 60 * 60 )
    RETURN __D & ":" & __H & ":" & __M & ":" & __S
```

### Decimal Hours to HH:MM

```dax
Hours Display =
    VAR __TotalHours = [Duration Hours]
    VAR __H = TRUNC( __TotalHours )
    VAR __M = ROUND( ( __TotalHours - __H ) * 60, 0 )
    RETURN FORMAT( __H, "00" ) & ":" & FORMAT( __M, "00" )
```

---

## Time Zone Conversion

Convert a time from one UTC offset to another:
```dax
TZ Convert = 
    VAR __SourceTime = TIME( 13, 0, 0 )  // 1:00 PM
    VAR __SourceTZOffset = -5 / 24       // EST (UTC-5)
    VAR __DestTZOffset = MAX( 'Time Zones'[UTC Offset] ) / 24
    VAR __UTCTime = __SourceTime - __SourceTZOffset
    VAR __Result = __UTCTime + __DestTZOffset
    RETURN __Result
```

---

## Last Refresh Timestamp

Create a timestamp showing when the model was last refreshed:
```dax
// Create a single-row table with UTC offset
// Timestamp = { -5 }  // Your UTC offset

Timestamp Column = UTCNOW() + [UTC Offset] / 24
```

---

## Unix Time Conversion

Convert Unix timestamp (seconds since 1970-01-01) to date:
```dax
Unix to Date = 
    VAR __UnixTime = [Unix Timestamp]
    VAR __UnixEpoch = DATE( 1970, 1, 1 )
    VAR __Days = DIVIDE( __UnixTime, 86400 )
    VAR __Result = __UnixEpoch + __Days
    RETURN __Result
```

Convert date back to Unix timestamp:
```dax
Date to Unix = 
    VAR __Date = [Date Value]
    VAR __UnixEpoch = DATE( 1970, 1, 1 )
    VAR __Result = ( __Date - __UnixEpoch ) * 86400
    RETURN __Result
```

---

## Shift Classification

Classify hours into work shifts:
```dax
Shift = 
    VAR __1stBegin = 9   // 9 AM
    VAR __2ndBegin = 17  // 5 PM
    VAR __3rdBegin = 1   // 1 AM
    VAR __Hour = HOUR( [Time] )
    VAR __Result = SWITCH(
        TRUE(),
        __Hour >= __1stBegin && __Hour < __2ndBegin, "First",
        __Hour >= __2ndBegin || __Hour < __3rdBegin, "Second",
        "Third"
    )
    RETURN __Result
```

---

## Net Work Duration

Calculate working hours between two times (excluding breaks):
```dax
Net Work Duration = 
    VAR __Start = MIN( 'Table'[Start Time] )
    VAR __End = MAX( 'Table'[End Time] )
    VAR __LunchStart = TIME( 12, 0, 0 )
    VAR __LunchEnd = TIME( 13, 0, 0 )
    VAR __TotalHours = ( __End - __Start ) * 24
    VAR __LunchOverlap = 
        MAX( 0, 
            MIN( __End, __LunchEnd ) - MAX( __Start, __LunchStart ) 
        ) * 24
    VAR __Result = __TotalHours - __LunchOverlap
    RETURN __Result
```

---

## Hours Breakdown by Period

Count minutes worked in each hour of the day:
```dax
// Requires an Hours table with Hour column (0-23)
Hours Breakdown = 
    VAR __Start = MIN( 'Events'[Start Time] )
    VAR __End = MAX( 'Events'[End Time] )
    VAR __CurrHour = MAX( 'Hours'[Hour] )
    VAR __HourStart = __CurrHour / 24
    VAR __HourEnd = ( __CurrHour + 1 ) / 24
    VAR __Overlap = MAX( 0, MIN( __End, __HourEnd ) - MAX( __Start, __HourStart ) )
    VAR __Result = __Overlap * 24 * 60  // Convert to minutes
    RETURN __Result
```

---

## Unix Timestamp (Milliseconds)

Convert Unix timestamp in milliseconds to datetime:
```dax
Unix MS to DateTime = 
    VAR __UnixMs = [Unix Timestamp MS]
    VAR __UnixEpoch = DATE( 1970, 1, 1 )
    VAR __Days = DIVIDE( __UnixMs, 86400000 )
    VAR __Result = __UnixEpoch + __Days
    RETURN __Result
```

Convert datetime to Unix milliseconds:
```dax
DateTime to Unix MS = 
    VAR __DateTime = [DateTime Value]
    VAR __UnixEpoch = DATE( 1970, 1, 1 )
    VAR __Result = ( __DateTime - __UnixEpoch ) * 86400000
    RETURN TRUNC( __Result )
```

---

## NETWORKDAYS - Work Days Only

Count business days between two dates (excluding weekends):

```dax
Work Days Between = 
    VAR __Start = MIN( 'Table'[Start Date] )
    VAR __End = MAX( 'Table'[End Date] )
    VAR __Result = NETWORKDAYS( __Start, __End, 1 )  // 1 = Week starts Monday
    RETURN __Result
```

With holidays:
```dax
Work Days Excluding Holidays = 
    VAR __Start = MIN( 'Table'[Start Date] )
    VAR __End = MAX( 'Table'[End Date] )
    VAR __Holidays = ALL( 'Holidays' )
    VAR __Result = NETWORKDAYS( __Start, __End, 1, __Holidays )
    RETURN __Result
```

> **Note**: `NETWORKDAYS` parameter 3 is week type: 1=Mon-Fri, 2=Sun-Sat, 11=Mon-Sun, etc.

---

## Shift Overlap Handling

Calculate hours when shifts span midnight:

```dax
Night Shift Hours = 
    VAR __Start = [Shift Start]  // e.g., 22:00 (10 PM)
    VAR __End = [Shift End]      // e.g., 06:00 (6 AM)
    VAR __Result = IF(
        __End < __Start,
        // Shift crosses midnight
        ( 1 - __Start + __End ) * 24,
        // Normal shift
        ( __End - __Start ) * 24
    )
    RETURN __Result
```

Classify shift type:
```dax
Shift Type = 
    VAR __Start = HOUR( [Start Time] )
    VAR __End = HOUR( [End Time] )
    VAR __Result = SWITCH(
        TRUE(),
        __Start >= 22 || __Start < 6, "Night",
        __Start >= 6 && __Start < 14, "Morning",
        __Start >= 14 && __Start < 22, "Afternoon",
        "Unknown"
    )
    RETURN __Result
```

---

## Hours Breakdown Across Days

Split a duration across multiple calendar days:

```dax
// Requires a Calendar table
Hours Per Day = 
    VAR __EventStart = MIN( 'Events'[Start DateTime] )
    VAR __EventEnd = MAX( 'Events'[End DateTime] )
    VAR __CurrentDate = MAX( 'Calendar'[Date] )
    VAR __DayStart = __CurrentDate
    VAR __DayEnd = __CurrentDate + 1
    
    // Calculate overlap with current day
    VAR __OverlapStart = MAX( __EventStart, __DayStart )
    VAR __OverlapEnd = MIN( __EventEnd, __DayEnd )
    VAR __Overlap = MAX( 0, __OverlapEnd - __OverlapStart )
    
    VAR __Result = __Overlap * 24  // Hours
    RETURN __Result
```

Total worked hours by day of week:
```dax
Hours by Weekday = 
    VAR __Table = ADDCOLUMNS(
        'TimeEntries',
        "__Day", FORMAT( [Date], "dddd" ),
        "__Hours", ( [End Time] - [Start Time] ) * 24
    )
    VAR __Result = SUMX( 
        FILTER( __Table, [__Day] = MAX( 'Weekdays'[Weekday] ) ), 
        [__Hours] 
    )
    RETURN __Result
```

---

## Meeting/Event Overlap Detection

Check if two events overlap:
```dax
Events Overlap = 
    VAR __Start1 = [Event1 Start]
    VAR __End1 = [Event1 End]
    VAR __Start2 = [Event2 Start]
    VAR __End2 = [Event2 End]
    VAR __Result = NOT( __End1 <= __Start2 || __End2 <= __Start1 )
    RETURN __Result
```

Calculate overlap duration:
```dax
Overlap Duration = 
    VAR __Start1 = [Event1 Start]
    VAR __End1 = [Event1 End]
    VAR __Start2 = [Event2 Start]
    VAR __End2 = [Event2 End]
    VAR __OverlapStart = MAX( __Start1, __Start2 )
    VAR __OverlapEnd = MIN( __End1, __End2 )
    VAR __Overlap = MAX( 0, __OverlapEnd - __OverlapStart )
    VAR __Result = __Overlap * 24 * 60  // Minutes
    RETURN __Result
```

---

## Time Constants Reference

| Value | Represents |
|-------|------------|
| `1` | 1 day |
| `1/24` | 1 hour |
| `1/24/60` | 1 minute |
| `1/24/60/60` | 1 second |
| `86400` | Seconds in a day |
| `86400000` | Milliseconds in a day |
| `3600` | Seconds in an hour |
| `3600000` | Milliseconds in an hour |
| `60` | Seconds in a minute |
| `60000` | Milliseconds in a minute |

---

## NETWORKDAYS Week Types

| Value | Description |
|-------|-------------|
| 1 | Mon-Fri (default) |
| 2 | Sun-Thu |
| 11 | Mon only off |
| 12 | Tue only off |
| ... | (continues to 17) |

---

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| Unix ms conversion | API timestamps from JavaScript |
| NETWORKDAYS | Business day calculations |
| Night shift handling | 24/7 operations, healthcare |
| Hours breakdown | Timesheet allocation |
| Overlap detection | Meeting conflicts, scheduling |
