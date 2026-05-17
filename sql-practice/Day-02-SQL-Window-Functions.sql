-- Query 1 — Rank customers by total spending
SELECT
    c.name,
    c.city,
    c.customer_segment,
    SUM(oi.quantity * oi.unit_price) AS total_spent,
    ROW_NUMBER() OVER (
        ORDER BY SUM(oi.quantity * oi.unit_price) DESC
    ) AS row_num,
    RANK() OVER (
        ORDER BY SUM(oi.quantity * oi.unit_price) DESC
    ) AS rank_num,
    DENSE_RANK() OVER (
        ORDER BY SUM(oi.quantity * oi.unit_price) DESC
    ) AS dense_rank_num
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.name, c.city, c.customer_segment
ORDER BY total_spent DESC;

--Query 2 — Rank customers by spending within each city
SELECT
    c.name,
    c.city,
    SUM(oi.quantity * oi.unit_price) AS total_spent,
    RANK() OVER (
        PARTITION BY c.city
        ORDER BY SUM(oi.quantity * oi.unit_price) DESC
    ) AS rank_within_city
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.name, c.city
ORDER BY c.city, rank_within_city;

--Query 3 — Top 2 customers per city only
WITH customer_city_rank AS (
    SELECT
        c.name,
        c.city,
        SUM(oi.quantity * oi.unit_price) AS total_spent,
        RANK() OVER (
            PARTITION BY c.city
            ORDER BY SUM(oi.quantity * oi.unit_price) DESC
        ) AS rank_within_city
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id, c.name, c.city
)
SELECT name, city, total_spent, rank_within_city
FROM customer_city_rank
WHERE rank_within_city <= 2
ORDER BY city, rank_within_city;

--Query 4 — Month over month order count change

WITH monthly_orders AS (
    SELECT
        DATE_TRUNC('month', order_date) AS order_month,
        COUNT(*) AS order_count
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT
    order_month,
    order_count,
    LAG(order_count) OVER (
        ORDER BY order_month
    ) AS previous_month_count,
    order_count - LAG(order_count) OVER (
        ORDER BY order_month
    ) AS month_over_month_change
FROM monthly_orders
ORDER BY order_month;

--Query 5 — Running total of revenue by date
SELECT
    o.order_date,
    SUM(oi.quantity * oi.unit_price) AS daily_revenue,
    SUM(SUM(oi.quantity * oi.unit_price)) OVER (
        ORDER BY o.order_date
        ROWS BETWEEN UNBOUNDED PRECEDING 
        AND CURRENT ROW
    ) AS running_total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY o.order_date
ORDER BY o.order_date;