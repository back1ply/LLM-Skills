# Market Basket Analysis

Product affinity, cross-sell recommendations, and bundle analysis patterns.

---

## Better Together (Product Affinity)

Find which products are frequently purchased together.

### Basic Product Pairs

```dax
Products Bought Together =
    VAR __CurrentProduct = MAX( 'Products'[ProductName] )

    -- Orders containing current product
    VAR __OrdersWithProduct = DISTINCT(
        SELECTCOLUMNS(
            FILTER( 'Sales', 'Sales'[ProductName] = __CurrentProduct ),
            "__OrderID", 'Sales'[OrderID]
        )
    )

    -- Other products in those orders
    VAR __OtherProducts = SUMMARIZE(
        FILTER(
            'Sales',
            'Sales'[OrderID] IN __OrdersWithProduct &&
            'Sales'[ProductName] <> __CurrentProduct
        ),
        'Sales'[ProductName],
        "__Count", COUNTROWS( 'Sales' )
    )

    -- Top paired product
    VAR __TopProduct = MAXX(
        TOPN( 1, __OtherProducts, [__Count], DESC ),
        'Sales'[ProductName]
    )

    RETURN __TopProduct
```

---

### Support (How Often Items Appear Together)

Percentage of transactions containing both items:

```dax
Support A and B =
    VAR __ProductA = "Laptop"
    VAR __ProductB = "Mouse"

    -- Orders with both products
    VAR __OrdersA = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] = __ProductA ),
        "__OrderID", [OrderID]
    ))

    VAR __OrdersB = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] = __ProductB ),
        "__OrderID", [OrderID]
    ))

    VAR __OrdersBoth = INTERSECT( __OrdersA, __OrdersB )

    -- Total orders
    VAR __TotalOrders = DISTINCTCOUNT( 'Sales'[OrderID] )

    -- Support = (Orders with A AND B) / (Total Orders)
    VAR __Support = DIVIDE( COUNTROWS( __OrdersBoth ), __TotalOrders, 0 )

    RETURN __Support
```

---

### Confidence (Conditional Probability)

If customer buys A, what's probability they buy B?

```dax
Confidence A → B =
    VAR __ProductA = "Laptop"
    VAR __ProductB = "Mouse"

    -- Orders with Product A
    VAR __OrdersA = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] = __ProductA ),
        "__OrderID", [OrderID]
    ))

    -- Orders with both A and B
    VAR __OrdersB = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] = __ProductB ),
        "__OrderID", [OrderID]
    ))

    VAR __OrdersBoth = INTERSECT( __OrdersA, __OrdersB )

    -- Confidence = P(B|A) = (A and B) / (A)
    VAR __Confidence = DIVIDE(
        COUNTROWS( __OrdersBoth ),
        COUNTROWS( __OrdersA ),
        0
    )

    RETURN __Confidence
```

**Interpretation:**
- Confidence = 0.65 means 65% of customers who buy Product A also buy Product B

---

### Lift (Association Strength)

How much more likely are items purchased together than by chance?

```dax
Lift A → B =
    VAR __ProductA = "Laptop"
    VAR __ProductB = "Mouse"

    VAR __Confidence = [Confidence A → B]

    -- Probability of B (overall)
    VAR __OrdersB = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] = __ProductB ),
        "__OrderID", [OrderID]
    ))
    VAR __TotalOrders = DISTINCTCOUNT( 'Sales'[OrderID] )
    VAR __ProbB = DIVIDE( COUNTROWS( __OrdersB ), __TotalOrders, 0 )

    -- Lift = Confidence / P(B)
    VAR __Lift = DIVIDE( __Confidence, __ProbB, 0 )

    RETURN __Lift
```

**Interpretation:**
- Lift = 1: No association (random chance)
- Lift > 1: Positive association (items purchased together more than expected)
- Lift < 1: Negative association (items purchased together less than expected)
- Lift = 2: Items are purchased together twice as often as expected

---

## Top Product Pairs

### Most Frequently Paired Products

```dax
Top Product Pairs =
    VAR __Pairs = GENERATE(
        DISTINCT( 'Sales'[ProductName] ),
        FILTER(
            DISTINCT( 'Sales'[ProductName] ),
            [ProductName] > EARLIER( 'Sales'[ProductName] )  -- Avoid duplicates
        )
    )

    VAR __PairsWithCounts = ADDCOLUMNS(
        __Pairs,
        "__ProductA", 'Sales'[ProductName],
        "__ProductB", [ProductName],
        "__Count",
            VAR __A = 'Sales'[ProductName]
            VAR __B = [ProductName]
            VAR __OrdersA = DISTINCT( SELECTCOLUMNS(
                FILTER( ALL( 'Sales' ), [ProductName] = __A ),
                "__OrderID", [OrderID]
            ))
            VAR __OrdersB = DISTINCT( SELECTCOLUMNS(
                FILTER( ALL( 'Sales' ), [ProductName] = __B ),
                "__OrderID", [OrderID]
            ))
            RETURN COUNTROWS( INTERSECT( __OrdersA, __OrdersB ) )
    )

    VAR __TopPairs = TOPN( 10, __PairsWithCounts, [__Count], DESC )

    RETURN __TopPairs
```

---

## Bundle Analysis

### Bundle Purchase Frequency

How often are 3+ items purchased together?

```dax
Bundle Count =
    VAR __BundleProducts = { "Laptop", "Mouse", "Keyboard" }

    VAR __OrdersWithAll = FILTER(
        SUMMARIZE( 'Sales', [OrderID] ),
        VAR __Order = [OrderID]
        VAR __ProductsInOrder = DISTINCT( SELECTCOLUMNS(
            FILTER( 'Sales', [OrderID] = __Order ),
            "__Product", [ProductName]
        ))
        -- Check if all bundle products are in this order
        RETURN COUNTROWS( EXCEPT( __BundleProducts, __ProductsInOrder ) ) = 0
    )

    RETURN COUNTROWS( __OrdersWithAll )
```

---

### Dynamic Bundle Builder

Find best N-product bundles:

```dax
Best 3-Product Bundle =
    VAR __N = 3

    -- Get all N-product combinations from orders
    VAR __Bundles = SUMMARIZE(
        FILTER(
            SUMMARIZE(
                'Sales',
                [OrderID],
                "__ProductCount", DISTINCTCOUNT( [ProductName] )
            ),
            [__ProductCount] >= __N
        ),
        [OrderID]
    )

    VAR __BundleFrequency = ADDCOLUMNS(
        __Bundles,
        "__Products",
            VAR __Order = [OrderID]
            RETURN CONCATENATEX(
                TOPN( __N,
                    DISTINCT( SELECTCOLUMNS(
                        FILTER( 'Sales', [OrderID] = __Order ),
                        "__Product", [ProductName]
                    )),
                    [__Product], ASC
                ),
                [__Product],
                ", "
            ),
        "__Revenue", SUMX( FILTER( 'Sales', [OrderID] = [OrderID] ), [Amount] )
    )

    -- Group identical bundles
    VAR __GroupedBundles = SUMMARIZE(
        __BundleFrequency,
        [__Products],
        "__Count", COUNTROWS( __BundleFrequency ),
        "__AvgRevenue", AVERAGE( [__Revenue] )
    )

    VAR __TopBundle = TOPN( 1, __GroupedBundles, [__Count], DESC )

    RETURN MAXX( __TopBundle, [__Products] )
```

---

## Cross-Sell Recommendations

### Recommended Products for Current Cart

```dax
Recommended for Cart =
    -- Products currently in cart (from slicer/selection)
    VAR __CartProducts = VALUES( 'Selection'[ProductName] )

    -- Orders containing any cart product
    VAR __RelevantOrders = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] IN __CartProducts ),
        "__OrderID", [OrderID]
    ))

    -- Products in those orders (excluding cart items)
    VAR __Candidates = SUMMARIZE(
        FILTER(
            'Sales',
            [OrderID] IN __RelevantOrders &&
            NOT( [ProductName] IN __CartProducts )
        ),
        [ProductName],
        "__Frequency", COUNTROWS( 'Sales' )
    )

    -- Calculate lift for each candidate
    VAR __Scored = ADDCOLUMNS(
        __Candidates,
        "__Lift",
            VAR __Product = [ProductName]
            VAR __OrdersWithProduct = DISTINCT( SELECTCOLUMNS(
                FILTER( ALL( 'Sales' ), [ProductName] = __Product ),
                "__OrderID", [OrderID]
            ))
            VAR __Together = COUNTROWS( INTERSECT( __RelevantOrders, __OrdersWithProduct ) )
            VAR __Support = DIVIDE( __Together, COUNTROWS( __RelevantOrders ), 0 )

            VAR __OverallSupport = DIVIDE(
                COUNTROWS( __OrdersWithProduct ),
                DISTINCTCOUNT( 'Sales'[OrderID] ),
                0
            )
            RETURN DIVIDE( __Support, __OverallSupport, 0 )
    )

    -- Return top recommendation
    VAR __TopRecommendation = TOPN( 1, __Scored, [__Lift], DESC )

    RETURN MAXX( __TopRecommendation, [ProductName] )
```

---

## Category Affinity

### Cross-Category Purchases

```dax
Category Affinity =
    VAR __CategoryA = MAX( 'Categories'[CategoryName] )

    -- Orders with current category
    VAR __OrdersWithCategory = DISTINCT( SELECTCOLUMNS(
        FILTER(
            'Sales',
            RELATED( 'Products'[Category] ) = __CategoryA
        ),
        "__OrderID", [OrderID]
    ))

    -- Other categories in those orders
    VAR __OtherCategories = SUMMARIZE(
        FILTER(
            'Sales',
            [OrderID] IN __OrdersWithCategory &&
            RELATED( 'Products'[Category] ) <> __CategoryA
        ),
        'Products'[Category],
        "__Count", COUNTROWS( 'Sales' )
    )

    -- Most common paired category
    RETURN MAXX(
        TOPN( 1, __OtherCategories, [__Count], DESC ),
        'Products'[Category]
    )
```

---

## Sequence Analysis

### Next Purchase Prediction

What do customers typically buy next?

```dax
Next Purchase Prediction =
    VAR __CurrentProduct = MAX( 'Products'[ProductName] )

    -- Customers who bought current product
    VAR __Customers = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] = __CurrentProduct ),
        "__CustomerID", [CustomerID],
        "__Date", [OrderDate]
    ))

    -- Their next purchases (after buying current product)
    VAR __NextPurchases = SUMMARIZE(
        GENERATE(
            __Customers,
            FILTER(
                'Sales',
                [CustomerID] = [__CustomerID] &&
                [OrderDate] > [__Date]
            )
        ),
        [ProductName],
        "__Count", COUNTROWS( 'Sales' )
    )

    -- Most common next purchase
    RETURN MAXX(
        TOPN( 1, __NextPurchases, [__Count], DESC ),
        [ProductName]
    )
```

---

## Time-Based Patterns

### Repeat Purchase Interval

Average days between repeat purchases of same product:

```dax
Repeat Purchase Interval =
    VAR __Product = MAX( 'Products'[ProductName] )

    VAR __Purchases = ADDCOLUMNS(
        FILTER( 'Sales', [ProductName] = __Product ),
        "__CustomerID", [CustomerID],
        "__Date", [OrderDate]
    )

    VAR __Intervals = ADDCOLUMNS(
        __Purchases,
        "__PrevDate",
            VAR __Cust = [__CustomerID]
            VAR __Date = [__Date]
            RETURN MAXX(
                FILTER( __Purchases, [__CustomerID] = __Cust && [__Date] < __Date ),
                [__Date]
            ),
        "__DaysSinceLast",
            VAR __Prev = [__PrevDate]
            RETURN IF( NOT( ISBLANK( __Prev ) ), [__Date] - __Prev, BLANK() )
    )

    RETURN AVERAGEX(
        FILTER( __Intervals, NOT( ISBLANK( [__DaysSinceLast] ) ) ),
        [__DaysSinceLast]
    )
```

---

## Cannibalization Analysis

### Product Substitution

Measure if one product steals sales from another:

```dax
Cannibalization Score =
    VAR __ProductA = "Product A"
    VAR __ProductB = "Product B"

    -- Customers who bought A
    VAR __CustomersA = DISTINCT( SELECTCOLUMNS(
        FILTER( 'Sales', [ProductName] = __ProductA ),
        "__CustomerID", [CustomerID]
    ))

    -- Of those, how many also bought B
    VAR __CustomersBoth = INTERSECT(
        __CustomersA,
        DISTINCT( SELECTCOLUMNS(
            FILTER( 'Sales', [ProductName] = __ProductB ),
            "__CustomerID", [CustomerID]
        ))
    )

    -- Cannibalization = overlap / customers of A
    RETURN DIVIDE( COUNTROWS( __CustomersBoth ), COUNTROWS( __CustomersA ), 0 )
```

**Interpretation:**
- Score = 0.8 means 80% of customers who buy A also buy B
- High score may indicate products are substitutes or complements

---

## Visual Recommendations

### Affinity Matrix

Create a product × product affinity matrix:

```dax
Affinity Score =
    VAR __ProductRow = MAX( 'ProductsRow'[ProductName] )
    VAR __ProductCol = MAX( 'ProductsCol'[ProductName] )

    VAR __Result = IF(
        __ProductRow = __ProductCol,
        BLANK(),  -- Diagonal
        VAR __OrdersRow = DISTINCT( SELECTCOLUMNS(
            FILTER( 'Sales', [ProductName] = __ProductRow ),
            "__OrderID", [OrderID]
        ))
        VAR __OrdersCol = DISTINCT( SELECTCOLUMNS(
            FILTER( 'Sales', [ProductName] = __ProductCol ),
            "__OrderID", [OrderID]
        ))
        VAR __Together = COUNTROWS( INTERSECT( __OrdersRow, __OrdersCol ) )
        VAR __Total = DISTINCTCOUNT( 'Sales'[OrderID] )
        RETURN DIVIDE( __Together, __Total, 0 )
    )
    RETURN __Result
```

Use with matrix visual:
- Rows: ProductsRow[ProductName]
- Columns: ProductsCol[ProductName]
- Values: [Affinity Score]
- Conditional formatting: Heat map

---

## Performance Optimization

Market basket analysis can be computationally expensive:

### Strategies

1. **Pre-compute common pairs** in a table
2. **Filter to recent transactions** (last 90 days)
3. **Limit to top N products** by volume
4. **Use SUMMARIZE** to reduce row counts early
5. **Cache intermediate tables** in variables

### Example: Optimized Better Together

```dax
Better Together (Optimized) =
    VAR __CurrentProduct = MAX( 'Products'[ProductName] )

    -- Only look at recent, high-volume products
    VAR __RecentSales = FILTER(
        'Sales',
        [OrderDate] >= TODAY() - 90 &&
        [ProductName] IN VALUES( 'TopProducts'[ProductName] )
    )

    -- Summarize first to reduce rows
    VAR __OrderSummary = SUMMARIZE(
        __RecentSales,
        [OrderID],
        [ProductName]
    )

    VAR __OrdersWithProduct = DISTINCT( SELECTCOLUMNS(
        FILTER( __OrderSummary, [ProductName] = __CurrentProduct ),
        "__OrderID", [OrderID]
    ))

    VAR __OtherProducts = SUMMARIZE(
        FILTER(
            __OrderSummary,
            [OrderID] IN __OrdersWithProduct &&
            [ProductName] <> __CurrentProduct
        ),
        [ProductName],
        "__Count", COUNTROWS( __OrderSummary )
    )

    RETURN MAXX(
        TOPN( 1, __OtherProducts, [__Count], DESC ),
        [ProductName]
    )
```

---

## Use Cases

| Scenario | Metric |
|----------|--------|
| Product recommendations | Lift, Confidence |
| Bundle pricing | Support (frequent together) |
| Cross-sell campaigns | Confidence A → B |
| Category placement | Category affinity |
| Inventory planning | Product pairs frequency |
| Promotion planning | Cannibalization score |

---

## See Also

- [Customer KPIs](customer-kpis.md) - Customer segmentation
- [Advanced & Complex Patterns](advanced-complex-patterns.md) - Complex table operations
- [Statistics Patterns](statistics-patterns.md) - Correlation analysis
