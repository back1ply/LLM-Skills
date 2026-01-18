# Project Patterns

Project management calculations using the No CALCULATE approach.

---

## Burndown Chart

Track remaining work over time in a sprint/project:

```dax
Remaining Work = 
    VAR __CurrentDate = MAX( 'Dates'[Date] )
    VAR __Table = FILTER( 
        ALL( 'Tasks' ), 
        [Completed Date] > __CurrentDate || ISBLANK( [Completed Date] )
    )
    VAR __Result = SUMX( __Table, [Story Points] )
    RETURN __Result
```

Ideal burndown line:

```dax
Ideal Burndown = 
    VAR __StartDate = MIN( ALL( 'Dates'[Date] ) )
    VAR __EndDate = MAX( ALL( 'Dates'[Date] ) )
    VAR __TotalDays = __EndDate - __StartDate
    VAR __CurrentDate = MAX( 'Dates'[Date] )
    VAR __DaysElapsed = __CurrentDate - __StartDate
    VAR __TotalPoints = SUMX( ALL( 'Tasks' ), [Story Points] )
    VAR __Result = __TotalPoints * ( 1 - DIVIDE( __DaysElapsed, __TotalDays ) )
    RETURN __Result
```

---

## Earned Value Management (EVM)

### Planned Value (PV) / Budgeted Cost of Work Scheduled (BCWS)

```dax
Planned Value = 
    VAR __CurrentDate = MAX( 'Dates'[Date] )
    VAR __Table = FILTER( 'Tasks', [Planned End Date] <= __CurrentDate )
    VAR __Result = SUMX( __Table, [Budgeted Cost] )
    RETURN __Result
```

### Earned Value (EV) / Budgeted Cost of Work Performed (BCWP)

```dax
Earned Value = 
    VAR __CurrentDate = MAX( 'Dates'[Date] )
    VAR __Table = FILTER( 
        'Tasks', 
        [Actual End Date] <= __CurrentDate && NOT( ISBLANK( [Actual End Date] ) )
    )
    VAR __Result = SUMX( __Table, [Budgeted Cost] )
    RETURN __Result
```

### Actual Cost (AC)

```dax
Actual Cost = 
    VAR __CurrentDate = MAX( 'Dates'[Date] )
    VAR __Table = FILTER( 'Costs', [Date] <= __CurrentDate )
    VAR __Result = SUMX( __Table, [Cost] )
    RETURN __Result
```

### Cost Variance (CV)

```dax
Cost Variance = 
    VAR __EV = [Earned Value]
    VAR __AC = [Actual Cost]
    VAR __Result = __EV - __AC
    RETURN __Result
```

Positive = under budget, Negative = over budget

### Schedule Variance (SV)

```dax
Schedule Variance = 
    VAR __EV = [Earned Value]
    VAR __PV = [Planned Value]
    VAR __Result = __EV - __PV
    RETURN __Result
```

Positive = ahead of schedule, Negative = behind schedule

### Cost Performance Index (CPI)

```dax
CPI = 
    VAR __EV = [Earned Value]
    VAR __AC = [Actual Cost]
    VAR __Result = DIVIDE( __EV, __AC, BLANK() )
    RETURN __Result
```

> 1 = under budget, < 1 = over budget

### Schedule Performance Index (SPI)

```dax
SPI = 
    VAR __EV = [Earned Value]
    VAR __PV = [Planned Value]
    VAR __Result = DIVIDE( __EV, __PV, BLANK() )
    RETURN __Result
```

> 1 = ahead of schedule, < 1 = behind schedule

---

## Task Completion Rate

```dax
Completion Rate = 
    VAR __Total = COUNTROWS( 'Tasks' )
    VAR __Completed = COUNTROWS( 
        FILTER( 'Tasks', [Status] = "Complete" ) 
    )
    VAR __Result = DIVIDE( __Completed, __Total, 0 )
    RETURN __Result
```

---

## Tasks Completed Per Period

```dax
Tasks Completed = 
    VAR __Table = FILTER( 'Tasks', NOT( ISBLANK( [Completed Date] ) ) )
    VAR __Result = COUNTROWS( __Table )
    RETURN __Result
```

---

## Overdue Tasks

```dax
Overdue Tasks = 
    VAR __Today = TODAY()
    VAR __Table = FILTER( 
        'Tasks', 
        [Due Date] < __Today && ISBLANK( [Completed Date] )
    )
    VAR __Result = COUNTROWS( __Table )
    RETURN __Result
```

---

## Average Days to Complete

```dax
Avg Days to Complete = 
    VAR __Table = FILTER( 'Tasks', NOT( ISBLANK( [Completed Date] ) ) )
    VAR __WithDays = ADDCOLUMNS(
        __Table,
        "__Days", [Completed Date] - [Start Date]
    )
    VAR __Result = AVERAGEX( __WithDays, [__Days] )
    RETURN __Result
```

---

## Resource Utilization

```dax
Resource Utilization = 
    VAR __ActualHours = SUMX( 'TimeEntries', [Hours] )
    VAR __AvailableHours = SUMX( 'Resources', [Weekly Hours] ) * [Weeks in Period]
    VAR __Result = DIVIDE( __ActualHours, __AvailableHours, 0 )
    RETURN __Result
```

---

## Velocity (Agile)

Story points completed per sprint:

```dax
Velocity = 
    VAR __Table = FILTER( 
        'Tasks', 
        [Status] = "Complete" && NOT( ISBLANK( [Sprint] ) )
    )
    VAR __Result = SUMX( __Table, [Story Points] )
    RETURN __Result
```

Rolling average velocity:

```dax
Avg Velocity = 
    VAR __CurrentSprint = MAX( 'Sprints'[Sprint Number] )
    VAR __SprintsBack = 3
    VAR __Sprints = FILTER( 
        ALL( 'Sprints' ), 
        [Sprint Number] > __CurrentSprint - __SprintsBack && 
        [Sprint Number] <= __CurrentSprint 
    )
    VAR __VelocityTable = ADDCOLUMNS(
        __Sprints,
        "__Velocity", 
        SUMX( 
            FILTER( 'Tasks', [Sprint] = EARLIER( [Sprint Name] ) && [Status] = "Complete" ),
            [Story Points]
        )
    )
    VAR __Result = AVERAGEX( __VelocityTable, [__Velocity] )
    RETURN __Result
```

---

## Estimate vs Actual

```dax
Estimate Accuracy = 
    VAR __Table = FILTER( 'Tasks', NOT( ISBLANK( [Actual Hours] ) ) )
    VAR __WithVariance = ADDCOLUMNS(
        __Table,
        "__Variance", ABS( [Estimated Hours] - [Actual Hours] )
    )
    VAR __TotalEstimated = SUMX( __WithVariance, [Estimated Hours] )
    VAR __TotalVariance = SUMX( __WithVariance, [__Variance] )
    VAR __Result = 1 - DIVIDE( __TotalVariance, __TotalEstimated, 0 )
    RETURN __Result
```

---

## Overworked Detection

Identify resources working excessive hours:

```dax
Is Overworked = 
    VAR __WeekNum = MAX( 'TimeEntries'[WeekNum] )
    VAR __Resource = MAX( 'TimeEntries'[Resource] )
    VAR __WeeklyHours = SUMX( 
        FILTER( ALL( 'TimeEntries' ), 
            [WeekNum] = __WeekNum && [Resource] = __Resource 
        ), 
        [Hours] 
    )
    VAR __Threshold = 50  // Adjust as needed
    VAR __Result = IF( __WeeklyHours > __Threshold, TRUE(), FALSE() )
    RETURN __Result
```

Count of overworked resources:

```dax
Overworked Count = 
    VAR __Threshold = 50
    VAR __WeeklyHours = ADDCOLUMNS(
        SUMMARIZE( 'TimeEntries', [Resource], [WeekNum] ),
        "__Hours", SUMX( 
            FILTER( 'TimeEntries', 
                [Resource] = EARLIER( [Resource] ) && 
                [WeekNum] = EARLIER( [WeekNum] ) 
            ), 
            [Hours] 
        )
    )
    VAR __Overworked = FILTER( __WeeklyHours, [__Hours] > __Threshold )
    VAR __Result = COUNTROWS( __Overworked )
    RETURN __Result
```

Total overtime hours (beyond threshold):

```dax
Overtime Hours = 
    VAR __Threshold = 40
    VAR __WeeklyHours = ADDCOLUMNS(
        SUMMARIZE( 'TimeEntries', [Resource], [WeekNum] ),
        "__Hours", CALCULATE( SUM( 'TimeEntries'[Hours] ) )
    )
    VAR __OvertimePerWeek = ADDCOLUMNS(
        __WeeklyHours,
        "__Overtime", MAX( 0, [__Hours] - __Threshold )
    )
    VAR __Result = SUMX( __OvertimePerWeek, [__Overtime] )
    RETURN __Result
```

> [!NOTE]
> This pattern uses `CALCULATE` inside `ADDCOLUMNS` to aggregate hours per resource/week. This is acceptable because CALCULATE is used only to populate the intermediate variable, not to modify filter context in the final aggregation. For a pure No-CALCULATE alternative, use `GROUPBY` with `CURRENTGROUP()` as shown in [Table Functions](./table-functions.md#groupby-better-performance).
>
> **Use case**: HR dashboards, project health monitoring, burnout risk identification.
