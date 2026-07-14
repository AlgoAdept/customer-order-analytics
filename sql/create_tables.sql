CREATE DATABASE IF NOT EXISTS CUSTOMER_ORDER_ANALYTICS;
USE DATABASE CUSTOMER_ORDER_ANALYTICS;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

CREATE TABLE IF NOT EXISTS BRONZE_ORDERS (
    order_id STRING,
    order_date DATE,
    ship_date DATE,
    ship_mode STRING,
    customer_name STRING,
    segment STRING,
    state STRING,
    country STRING,
    market STRING,
    region STRING,
    product_id STRING,
    category STRING,
    sub_category STRING,
    product_name STRING,
    sales NUMBER(12,2),
    quantity NUMBER(10,0),
    discount NUMBER(6,4),
    profit NUMBER(12,2),
    shipping_cost NUMBER(12,2),
    order_priority STRING,
    year NUMBER(10,0)
);

CREATE TABLE IF NOT EXISTS SILVER_ORDERS (
    order_id STRING,
    order_date DATE,
    ship_date DATE,
    ship_mode STRING,
    customer_name STRING,
    segment STRING,
    state STRING,
    country STRING,
    market STRING,
    region STRING,
    product_id STRING,
    category STRING,
    sub_category STRING,
    product_name STRING,
    sales NUMBER(12,2),
    quantity NUMBER(10,0),
    discount NUMBER(6,4),
    profit NUMBER(12,2),
    shipping_cost NUMBER(12,2),
    order_priority STRING,
    year NUMBER(10,0)
);

CREATE TABLE IF NOT EXISTS DIM_CUSTOMER (
    customer_id NUMBER,
    customer_name STRING,
    segment STRING
);

CREATE TABLE IF NOT EXISTS DIM_PRODUCT (
    product_id NUMBER,
    product_name STRING,
    category STRING,
    sub_category STRING
);

CREATE TABLE IF NOT EXISTS DIM_LOCATION (
    location_id NUMBER,
    country STRING,
    state STRING,
    market STRING,
    region STRING
);

CREATE TABLE IF NOT EXISTS DIM_DATE (
    date_id NUMBER,
    full_date DATE,
    year NUMBER,
    quarter NUMBER,
    month NUMBER,
    month_name STRING,
    day NUMBER,
    weekday STRING
);

CREATE TABLE IF NOT EXISTS FACT_SALES (
    order_id STRING,
    customer_id NUMBER,
    product_id NUMBER,
    location_id NUMBER,
    date_id NUMBER,
    sales NUMBER(12,2),
    profit NUMBER(12,2),
    quantity NUMBER(10,0),
    discount NUMBER(6,4),
    shipping_cost NUMBER(12,2)
);

CREATE TABLE IF NOT EXISTS CUSTOMER_METRICS (
    customer_name STRING,
    segment STRING,
    market STRING,
    region STRING,
    country STRING,
    total_orders NUMBER,
    total_sales NUMBER(12,2),
    total_profit NUMBER(12,2),
    profit_margin_pct NUMBER(10,2),
    total_quantity NUMBER,
    average_order_value NUMBER(12,2),
    average_discount NUMBER(10,4),
    first_order_date DATE,
    last_order_date DATE,
    customer_lifespan_days NUMBER,
    repeat_customer STRING
);
