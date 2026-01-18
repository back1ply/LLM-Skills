# Distance and Space Patterns

Geographic and spatial calculations using the No CALCULATE approach.

---

## Shared Patterns Note
> **Note**: The Haversine formula logic is repeated in several patterns below (Nearest Store, Distance, Radius) to make each pattern self-contained and copy-paste friendly.

## ATAN2 Implementation

DAX lacks a native ATAN2 function. This pattern implements it:

```dax
ATAN2 = 
    VAR __Y = [Y Value]
    VAR __X = [X Value]
    VAR __PI = PI()
    VAR __Result = SWITCH(
        TRUE(),
        __X > 0, ATAN( __Y / __X ),
        __X < 0 && __Y >= 0, ATAN( __Y / __X ) + __PI,
        __X < 0 && __Y < 0, ATAN( __Y / __X ) - __PI,
        __X = 0 && __Y > 0, __PI / 2,
        __X = 0 && __Y < 0, -__PI / 2,
        BLANK()  // X=0, Y=0 is undefined
    )
    RETURN __Result
```

---

## Haversine Distance

Calculate the distance between two geographic points (in kilometers):

```dax
Haversine Distance KM = 
    VAR __EarthRadius = 6371  // km (use 3959 for miles)
    VAR __Lat1 = RADIANS( [Latitude 1] )
    VAR __Lat2 = RADIANS( [Latitude 2] )
    VAR __Lon1 = RADIANS( [Longitude 1] )
    VAR __Lon2 = RADIANS( [Longitude 2] )
    VAR __DeltaLat = __Lat2 - __Lat1
    VAR __DeltaLon = __Lon2 - __Lon1
    VAR __A = SIN( __DeltaLat / 2 ) ^ 2 + 
              COS( __Lat1 ) * COS( __Lat2 ) * SIN( __DeltaLon / 2 ) ^ 2
    VAR __C = 2 * ASIN( SQRT( __A ) )
    VAR __Result = __EarthRadius * __C
    RETURN __Result
```

For miles, change `__EarthRadius` to `3959`.

---

## Distance Between Points (Euclidean)

For flat/Cartesian coordinates:

```dax
Euclidean Distance = 
    VAR __X1 = [X1]
    VAR __Y1 = [Y1]
    VAR __X2 = [X2]
    VAR __Y2 = [Y2]
    VAR __DeltaX = __X2 - __X1
    VAR __DeltaY = __Y2 - __Y1
    VAR __Result = SQRT( __DeltaX ^ 2 + __DeltaY ^ 2 )
    RETURN __Result
```

3D distance:
```dax
3D Distance = 
    VAR __DeltaX = [X2] - [X1]
    VAR __DeltaY = [Y2] - [Y1]
    VAR __DeltaZ = [Z2] - [Z1]
    VAR __Result = SQRT( __DeltaX ^ 2 + __DeltaY ^ 2 + __DeltaZ ^ 2 )
    RETURN __Result
```

---

## Bearing (Direction Between Points)

Calculate the compass bearing from point 1 to point 2:

```dax
Bearing = 
    VAR __Lat1 = RADIANS( [Latitude 1] )
    VAR __Lat2 = RADIANS( [Latitude 2] )
    VAR __DeltaLon = RADIANS( [Longitude 2] - [Longitude 1] )
    VAR __Y = SIN( __DeltaLon ) * COS( __Lat2 )
    VAR __X = COS( __Lat1 ) * SIN( __Lat2 ) - 
              SIN( __Lat1 ) * COS( __Lat2 ) * COS( __DeltaLon )
    // Using ATAN2 pattern
    VAR __PI = PI()
    VAR __ATAN2 = SWITCH(
        TRUE(),
        __X > 0, ATAN( __Y / __X ),
        __X < 0 && __Y >= 0, ATAN( __Y / __X ) + __PI,
        __X < 0 && __Y < 0, ATAN( __Y / __X ) - __PI,
        __X = 0 && __Y > 0, __PI / 2,
        __X = 0 && __Y < 0, -__PI / 2,
        0
    )
    VAR __Bearing = MOD( DEGREES( __ATAN2 ) + 360, 360 )
    RETURN __Bearing
```

---

## Cartesian to Polar Coordinates

```dax
Polar Radius = SQRT( [X] ^ 2 + [Y] ^ 2 )

Polar Angle = 
    VAR __X = [X]
    VAR __Y = [Y]
    VAR __PI = PI()
    VAR __ATAN2 = SWITCH(
        TRUE(),
        __X > 0, ATAN( __Y / __X ),
        __X < 0 && __Y >= 0, ATAN( __Y / __X ) + __PI,
        __X < 0 && __Y < 0, ATAN( __Y / __X ) - __PI,
        __X = 0 && __Y > 0, __PI / 2,
        __X = 0 && __Y < 0, -__PI / 2,
        0
    )
    VAR __Result = DEGREES( __ATAN2 )
    RETURN __Result
```

---

## Polar to Cartesian Coordinates

```dax
Cartesian X = [Radius] * COS( RADIANS( [Angle] ) )
Cartesian Y = [Radius] * SIN( RADIANS( [Angle] ) )
```

---

## Nearest Location

Find the nearest store/location to a customer:

```dax
Nearest Store = 
    VAR __CustLat = MAX( 'Customers'[Latitude] )
    VAR __CustLon = MAX( 'Customers'[Longitude] )
    VAR __EarthRadius = 6371
    VAR __Stores = ADDCOLUMNS(
        ALL( 'Stores' ),
        "__Distance",
        VAR __Lat1 = RADIANS( __CustLat )
        VAR __Lat2 = RADIANS( [Latitude] )
        VAR __DeltaLat = __Lat2 - __Lat1
        VAR __DeltaLon = RADIANS( [Longitude] - __CustLon )
        VAR __A = SIN( __DeltaLat / 2 ) ^ 2 + 
                  COS( __Lat1 ) * COS( __Lat2 ) * SIN( __DeltaLon / 2 ) ^ 2
        RETURN __EarthRadius * 2 * ASIN( SQRT( __A ) )
    )
    VAR __MinDist = MINX( __Stores, [__Distance] )
    VAR __Result = MAXX( FILTER( __Stores, [__Distance] = __MinDist ), [Store Name] )
    RETURN __Result
```

---

## Distance to Nearest

Return the distance to the nearest location:

```dax
Distance to Nearest = 
    VAR __CustLat = MAX( 'Customers'[Latitude] )
    VAR __CustLon = MAX( 'Customers'[Longitude] )
    VAR __EarthRadius = 6371
    VAR __Distances = ADDCOLUMNS(
        ALL( 'Stores' ),
        "__Distance",
        VAR __Lat1 = RADIANS( __CustLat )
        VAR __Lat2 = RADIANS( [Latitude] )
        VAR __DeltaLat = __Lat2 - __Lat1
        VAR __DeltaLon = RADIANS( [Longitude] - __CustLon )
        VAR __A = SIN( __DeltaLat / 2 ) ^ 2 + 
                  COS( __Lat1 ) * COS( __Lat2 ) * SIN( __DeltaLon / 2 ) ^ 2
        RETURN __EarthRadius * 2 * ASIN( SQRT( __A ) )
    )
    VAR __Result = MINX( __Distances, [__Distance] )
    RETURN __Result
```

---

## Locations Within Radius

Count locations within X kilometers:

```dax
Stores Within 10km = 
    VAR __CustLat = MAX( 'Customers'[Latitude] )
    VAR __CustLon = MAX( 'Customers'[Longitude] )
    VAR __Radius = 10  // km
    VAR __EarthRadius = 6371
    VAR __NearbyStores = FILTER(
        ADDCOLUMNS(
            ALL( 'Stores' ),
            "__Distance",
            VAR __Lat1 = RADIANS( __CustLat )
            VAR __Lat2 = RADIANS( [Latitude] )
            VAR __DeltaLat = __Lat2 - __Lat1
            VAR __DeltaLon = RADIANS( [Longitude] - __CustLon )
            VAR __A = SIN( __DeltaLat / 2 ) ^ 2 + 
                      COS( __Lat1 ) * COS( __Lat2 ) * SIN( __DeltaLon / 2 ) ^ 2
            RETURN __EarthRadius * 2 * ASIN( SQRT( __A ) )
        ),
        [__Distance] <= __Radius
    )
    VAR __Result = COUNTROWS( __NearbyStores )
    RETURN __Result
```

---

## Eastings/Northings (UTM) Conversion

Convert latitude/longitude to UTM-style grid coordinates (simplified):

```dax
UTM Easting = 
    VAR __Lon = [Longitude]
    VAR __Lat = [Latitude]
    VAR __Zone = TRUNC( ( __Lon + 180 ) / 6 ) + 1
    VAR __LonOrigin = ( __Zone - 1 ) * 6 - 180 + 3
    VAR __k0 = 0.9996
    VAR __a = 6378137  // WGS84 equatorial radius
    VAR __e2 = 0.00669438  // WGS84 eccentricity squared
    VAR __LonRad = RADIANS( __Lon - __LonOrigin )
    VAR __LatRad = RADIANS( __Lat )
    VAR __N = __a / SQRT( 1 - __e2 * SIN( __LatRad ) ^ 2 )
    VAR __T = TAN( __LatRad ) ^ 2
    VAR __C = __e2 / ( 1 - __e2 ) * COS( __LatRad ) ^ 2
    VAR __A = COS( __LatRad ) * __LonRad
    VAR __Easting = __k0 * __N * ( __A + ( 1 - __T + __C ) * __A ^ 3 / 6 ) + 500000
    RETURN __Easting
```

> **Note**: Full UTM conversion is complex. For production use, consider Power Query or pre-converted data.

---

## Transitive Closure (Network Paths)

Find all reachable nodes in a graph/network. Useful for org charts, supply chains, or any hierarchical data.

```dax
Reachable Nodes = 
    VAR __StartNode = MAX( 'Nodes'[Node] )
    VAR __Edges = ALL( 'Edges' )
    
    // Level 1: Direct connections
    VAR __L1 = SELECTCOLUMNS(
        FILTER( __Edges, [From] = __StartNode ),
        "__Node", [To]
    )
    
    // Level 2: One hop away
    VAR __L2 = SELECTCOLUMNS(
        FILTER( __Edges, [From] IN __L1 ),
        "__Node", [To]
    )
    
    // Level 3: Two hops away
    VAR __L3 = SELECTCOLUMNS(
        FILTER( __Edges, [From] IN __L2 ),
        "__Node", [To]
    )
    
    // Combine all reachable (up to 3 hops)
    VAR __All = DISTINCT( UNION( __L1, __L2, __L3 ) )
    RETURN CONCATENATEX( __All, [__Node], ", " )
```

Path exists check:
```dax
Path Exists = 
    VAR __From = MAX( 'Selection'[From Node] )
    VAR __To = MAX( 'Selection'[To Node] )
    VAR __Edges = ALL( 'Edges' )
    
    // Direct connection
    VAR __Direct = NOT( ISEMPTY( 
        FILTER( __Edges, [From] = __From && [To] = __To ) 
    ))
    
    // One hop
    VAR __OneHop = NOT( ISEMPTY(
        FILTER( __Edges,
            [From] IN SELECTCOLUMNS( 
                FILTER( __Edges, [From] = __From ), "__N", [To] 
            ) && [To] = __To
        )
    ))
    
    RETURN __Direct || __OneHop
```

---

## Box Sizes and Volume

Calculate volume and dimensional weight for shipping:

```dax
Volume Cubic = [Length] * [Width] * [Height]

Dimensional Weight KG = 
    VAR __Volume = [Length] * [Width] * [Height]  // cm
    VAR __DimFactor = 5000  // Standard DIM factor
    VAR __Result = DIVIDE( __Volume, __DimFactor )
    RETURN __Result

Billable Weight = 
    VAR __Actual = [Actual Weight KG]
    VAR __Dim = [Dimensional Weight KG]
    RETURN MAX( __Actual, __Dim )
```

Container fit check:
```dax
Fits In Container = 
    VAR __ItemL = [Item Length]
    VAR __ItemW = [Item Width]
    VAR __ItemH = [Item Height]
    VAR __ContL = MAX( 'Container'[Length] )
    VAR __ContW = MAX( 'Container'[Width] )
    VAR __ContH = MAX( 'Container'[Height] )
    
    // Check all rotations
    VAR __Fits = 
        ( __ItemL <= __ContL && __ItemW <= __ContW && __ItemH <= __ContH ) ||
        ( __ItemL <= __ContL && __ItemH <= __ContW && __ItemW <= __ContH ) ||
        ( __ItemW <= __ContL && __ItemL <= __ContW && __ItemH <= __ContH ) ||
        ( __ItemW <= __ContL && __ItemH <= __ContW && __ItemL <= __ContH ) ||
        ( __ItemH <= __ContL && __ItemL <= __ContW && __ItemW <= __ContH ) ||
        ( __ItemH <= __ContL && __ItemW <= __ContW && __ItemL <= __ContH )
    RETURN __Fits
```

---

## N Nearest Locations

Find the top N closest locations:

```dax
Top 3 Nearest Stores = 
    VAR __CustLat = MAX( 'Customers'[Latitude] )
    VAR __CustLon = MAX( 'Customers'[Longitude] )
    VAR __N = 3
    VAR __EarthRadius = 6371
    
    VAR __WithDistance = ADDCOLUMNS(
        ALL( 'Stores' ),
        "__Distance",
        VAR __Lat1 = RADIANS( __CustLat )
        VAR __Lat2 = RADIANS( [Latitude] )
        VAR __DeltaLat = __Lat2 - __Lat1
        VAR __DeltaLon = RADIANS( [Longitude] - __CustLon )
        VAR __A = SIN( __DeltaLat / 2 ) ^ 2 + 
                  COS( __Lat1 ) * COS( __Lat2 ) * SIN( __DeltaLon / 2 ) ^ 2
        RETURN __EarthRadius * 2 * ASIN( SQRT( __A ) )
    )
    
    VAR __TopN = TOPN( __N, __WithDistance, [__Distance], ASC )
    VAR __Result = CONCATENATEX( __TopN, [Store Name] & " (" & FORMAT( [__Distance], "0.0" ) & " km)", ", " )
    RETURN __Result
```

---

## Trigonometry Reference

| Function | Purpose |
|----------|---------|
| `SIN(x)` | Sine (x in radians) |
| `COS(x)` | Cosine (x in radians) |
| `TAN(x)` | Tangent (x in radians) |
| `ASIN(x)` | Arc sine (returns radians) |
| `ACOS(x)` | Arc cosine (returns radians) |
| `ATAN(x)` | Arc tangent (returns radians) |
| `RADIANS(degrees)` | Convert degrees to radians |
| `DEGREES(radians)` | Convert radians to degrees |
| `PI()` | Returns π (~3.14159) |
| `SQRT(x)` | Square root |
