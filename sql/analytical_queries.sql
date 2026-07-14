-- Top Customers by Revenue
SELECT customer_name, total_sales
FROM CUSTOMER_METRICS
ORDER BY total_sales DESC
LIMIT 10;

-- Revenue by Region
SELECT region, SUM(total_sales) AS revenue
FROM CUSTOMER_METRICS
GROUP BY region
ORDER BY revenue DESC;

-- Revenue by Segment
SELECT segment, SUM(total_sales) AS revenue
FROM CUSTOMER_METRICS
GROUP BY segment
ORDER BY revenue DESC;

-- Monthly Sales
SELECT DATE_TRUNC('month', first_order_date) AS order_month, SUM(total_sales) AS revenue
FROM CUSTOMER_METRICS
GROUP BY 1
ORDER BY 1;

-- Average Order Value
SELECT AVG(average_order_value) AS avg_order_value
FROM CUSTOMER_METRICS;

-- Repeat Customers
SELECT repeat_customer, COUNT(*) AS customer_count
FROM CUSTOMER_METRICS
GROUP BY repeat_customer;

-- Top Products
SELECT product_name, SUM(sales) AS revenue
FROM FACT_SALES
JOIN DIM_PRODUCT USING (product_id)
GROUP BY product_name
ORDER BY revenue DESC
LIMIT 10;

-- Profit by Category
SELECT category, SUM(profit) AS total_profit
FROM FACT_SALES
JOIN DIM_PRODUCT USING (product_id)
GROUP BY category
ORDER BY total_profit DESC;

-- Customer Lifetime Value
SELECT customer_name, total_profit AS customer_lifetime_value
FROM CUSTOMER_METRICS
ORDER BY customer_lifetime_value DESC
LIMIT 10;
