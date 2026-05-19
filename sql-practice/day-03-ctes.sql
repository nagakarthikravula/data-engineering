WITH customer_summary AS (
    SELECT
        c.customer_id,
        c.name,
        c.city,
        c.customer_segment,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.quantity * oi.unit_price) AS total_revenue,
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY 
        c.customer_id, c.name, 
        c.city, c.customer_segment
)
SELECT
    name,
    city,
    customer_segment,
    total_orders,
    ROUND(total_revenue, 2) AS total_revenue,
    first_order_date,
    last_order_date,
    last_order_date - first_order_date AS days_as_customer
FROM customer_summary
ORDER BY total_revenue DESC;

--2
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY DATE_TRUNC('month', o.order_date)
),
revenue_with_change AS (
    SELECT
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY month) AS prev_revenue,
        revenue - LAG(revenue) OVER (ORDER BY month) AS revenue_change
    FROM monthly_revenue
),
revenue_ranked AS (
    SELECT
        month,
        revenue,
        prev_revenue,
        revenue_change,
        RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
    FROM revenue_with_change
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(prev_revenue, 2) AS prev_revenue,
    ROUND(revenue_change, 2) AS revenue_change,
    revenue_rank,
    CASE
        WHEN revenue_change > 0 THEN 'Growth'
        WHEN revenue_change < 0 THEN 'Decline'
        WHEN revenue_change = 0 THEN 'Flat'
        ELSE 'First Month'
    END AS trend
FROM revenue_ranked
ORDER BY month;
--3
WITH RECURSIVE date_series AS (
    -- Anchor: starting point
    SELECT DATE '2024-01-01' AS date_value
    
    UNION ALL
    
    -- Recursive: adds 1 day each time
    SELECT date_value + INTERVAL '1 day'
    FROM date_series
    WHERE date_value < DATE '2024-01-31'
)
SELECT date_value
FROM date_series
ORDER BY date_value;
--4
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' AS date_value
    UNION ALL
    SELECT date_value + INTERVAL '1 day'
    FROM date_series
    WHERE date_value < DATE '2024-12-31'
),
daily_orders AS (
    SELECT
        order_date,
        COUNT(*) AS order_count,
        SUM(oi.quantity * oi.unit_price) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY order_date
)
SELECT
    ds.date_value AS date,
    COALESCE(do.order_count, 0) AS orders,
    COALESCE(ROUND(do.daily_revenue, 2), 0) AS revenue
FROM date_series ds
LEFT JOIN daily_orders do 
    ON ds.date_value = do.order_date
ORDER BY ds.date_value;
--5
WITH customer_metrics AS (
    SELECT
        c.customer_id,
        c.name,
        c.customer_segment,
        c.city,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity * oi.unit_price) AS total_spent,
        MAX(o.order_date) AS last_order_date,
        CURRENT_DATE - MAX(o.order_date) AS days_since_last_order
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id, c.name, c.customer_segment, c.city
),
customer_with_ranks AS (
    SELECT
        *,
        NTILE(4) OVER (ORDER BY total_spent DESC) AS spending_quartile,
        ROUND(AVG(total_spent) OVER (PARTITION BY city), 2) AS avg_spending_in_city,
        RANK() OVER (PARTITION BY customer_segment ORDER BY total_spent DESC) AS rank_in_segment
    FROM customer_metrics
)
SELECT
    name,
    city,
    customer_segment,
    order_count,
    ROUND(total_spent, 2) AS total_spent,
    days_since_last_order,
    spending_quartile,
    avg_spending_in_city,
    rank_in_segment,
    CASE spending_quartile
        WHEN 1 THEN 'VIP Customer'
        WHEN 2 THEN 'Loyal Customer'
        WHEN 3 THEN 'Regular Customer'
        WHEN 4 THEN 'At Risk Customer'
    END AS customer_label
FROM customer_with_ranks
ORDER BY total_spent DESC;