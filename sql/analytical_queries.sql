-- Top Customers by Revenue
SELECT customer_name, total_sales AS revenue
FROM CUSTOMER_METRICS
ORDER BY revenue DESC
LIMIT 10;

-- Revenue by Region
SELECT l.region, SUM(f.sales) AS revenue
FROM FACT_SALES f
JOIN DIM_LOCATION l ON f.location_id = l.location_id
GROUP BY l.region
ORDER BY revenue DESC;

-- Revenue by Segment
SELECT c.segment, SUM(f.sales) AS revenue
FROM FACT_SALES f
JOIN DIM_CUSTOMER c ON f.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;

-- Monthly Sales Trend
SELECT DATE_TRUNC('month', d.full_date) AS order_month, SUM(f.sales) AS revenue
FROM FACT_SALES f
JOIN DIM_DATE d ON f.date_id = d.date_id
GROUP BY 1
ORDER BY 1;

-- Average Order Value
SELECT AVG(order_sales) AS avg_order_value
FROM (
    SELECT order_id, SUM(sales) AS order_sales
    FROM FACT_SALES
    GROUP BY order_id
) order_totals;

-- Repeat Customers
SELECT repeat_customer, COUNT(*) AS customer_count
FROM CUSTOMER_METRICS
GROUP BY repeat_customer
ORDER BY customer_count DESC;

-- Top Products by Sales
SELECT p.product_name, SUM(f.sales) AS revenue
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10;

-- Profit by Category
SELECT p.category, SUM(f.profit) AS total_profit
FROM FACT_SALES f
JOIN DIM_PRODUCT p ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY total_profit DESC;

-- Customer Lifetime Value
SELECT customer_name, customer_lifetime_value
FROM CUSTOMER_METRICS
ORDER BY customer_lifetime_value DESC
LIMIT 10;
