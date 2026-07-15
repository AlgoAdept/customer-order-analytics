# Customer Order Analytics

## Project Overview

Customer Order Analytics is an end-to-end data engineering project that transforms raw customer order data into a structured analytical dataset for business reporting. The pipeline follows Medallion Architecture and loads the processed data into Snowflake for downstream analysis.

## Business Problem

Organizations need a reliable way to understand customer purchasing behavior, revenue contribution, product performance, and repeat buying patterns. This project addresses that need by turning raw transaction data into curated datasets that support analytical reporting and decision-making.

## Solution Overview

The solution moves data through three layers:

1. Bronze: raw source data stored as a CSV file
2. Silver: cleaned and standardized data prepared for analysis
3. Gold: star schema tables and business metrics designed for reporting

The process is automated with Python scripts and delivered to Snowflake for storage and query access.

## Project Architecture

```mermaid
flowchart LR
    A[Raw SuperStore Dataset] --> B[Bronze Layer]
    B --> C[Silver Layer]
    C --> D[Gold Layer]
    D --> E[Snowflake Data Warehouse]
    E --> F[SQL Analytical Reports]
```

## Medallion Architecture

The project uses simplified Medallion Architecture to improve data quality progressively as it moves from raw to curated forms.

```mermaid
flowchart TD
    A[Bronze Layer] --> B[Silver Layer]
    B --> C[Gold Layer]
```

| Layer | Purpose |
| --- | --- |
| Bronze | Stores the original raw CSV data without modification |
| Silver | Cleans, validates, and standardizes data for analytics |
| Gold | Produces reporting-ready tables and metrics |

## Star Schema Design

The Gold layer uses a star schema to support efficient analytical reporting. Dimension tables describe customers, products, locations, and dates, while the fact table stores transactional sales data.

```mermaid
erDiagram
    DIM_CUSTOMER ||--o{ FACT_SALES : purchases
    DIM_PRODUCT ||--o{ FACT_SALES : appears_in
    DIM_LOCATION ||--o{ FACT_SALES : located_in
    DIM_DATE ||--o{ FACT_SALES : ordered_on

    DIM_CUSTOMER {
        int customer_id
        string customer_name
        string segment
    }

    DIM_PRODUCT {
        int product_id
        string product_name
        string category
        string sub_category
    }

    DIM_LOCATION {
        int location_id
        string country
        string state
        string market
        string region
    }

    DIM_DATE {
        int date_id
        date full_date
        int year
        int quarter
    }

    FACT_SALES {
        string order_id
        int customer_id
        int product_id
        int location_id
        int date_id
        float sales
        float profit
    }
```

A star schema is used because it simplifies reporting, improves query performance, and makes business analysis easier to understand.

## Technology Stack

- Python
- Pandas
- Snowflake
- Snowflake SQL
- Git and GitHub
- VS Code

## Project Folder Structure

```text
Customer-Order-Analytics/
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── docs/
├── notebooks/
├── scripts/
│   ├── data_cleaning.py
│   ├── transformation.py
│   └── snowflake_loader.py
├── sql/
├── README.md
└── requirements.txt
```

## ETL Pipeline Workflow

```mermaid
flowchart LR
    A[Raw Data] --> B[Data Cleaning]
    B --> C[Standardized Silver Data]
    C --> D[Transformation to Gold Layer]
    D --> E[CSV Outputs]
    E --> F[Snowflake Load]
```

The workflow is implemented through the following scripts:

- scripts/data_cleaning.py for Bronze-to-Silver processing
- scripts/transformation.py for Gold-layer transformations and metrics
- scripts/snowflake_loader.py for automated Snowflake loading

## Snowflake Integration

The project connects to Snowflake and performs the following steps automatically:

- validates Snowflake connection settings
- creates the target database and schema if needed
- creates the required tables
- loads Bronze, Silver, and Gold data into Snowflake
- validates row counts after loading


## 📈 Analytical Reports & Business Insights

These reports turn the curated analytical data into decision-ready views for business users. Each report helps answer a practical question about customer value, regional performance, product demand, and profitability.

### Top Customers by Revenue

This report highlights the customers contributing the largest share of revenue. It is useful for identifying high-value accounts, prioritizing account management, and understanding which customers drive the most business impact.

**Screenshot**

![Top Customers by Revenue](results/top_customers_by_revenue.png)

**Business Insight**
- Business users can identify their most valuable customers and focus retention or growth efforts on those accounts.

### Revenue by Region

This report summarizes sales performance across different geographic regions. It helps stakeholders understand where revenue is concentrated and which markets may need additional support or investment.

**Screenshot**

![Revenue by Region](results/revenue_by_region.png)

**Business Insight**
- Business users can see where revenue is strongest or weakest geographically and adjust sales coverage or regional strategy accordingly.

### Revenue by Segment

This report breaks down revenue by customer segment such as consumer, corporate, or home office. It is valuable for understanding which customer groups are contributing most to the business and where growth opportunities may exist.

**Screenshot**

![Revenue by Segment](results/revenue_by_segment.png)

**Business Insight**
- Business users can compare customer segment performance and tailor marketing or service strategies to the most profitable groups.

### Monthly Sales Trend

This report shows how sales change over time across months or periods. It helps teams identify seasonal patterns, monitor growth, and evaluate whether recent performance is improving or declining.

**Screenshot**

![Monthly Sales Trend](results/monthly_sales_trend.png)

**Business Insight**
- Business users can spot trends in performance over time and plan forecasting, inventory, or promotional activity more effectively.

### Top Products by Sales

This report identifies the products generating the most sales volume or revenue. It is helpful for recognizing strong-performing items and understanding which offerings are most important to the business.

**Screenshot**

![Top Products by Sales](results/top_products.png)

**Business Insight**
- Business users can pinpoint the products that matter most to revenue and prioritize merchandising or promotional strategies around them.

### Profit by Category

This report examines profitability across product categories. It supports decisions around category focus, cost control, and identifying where the business is creating the most value.

**Screenshot**

![Profit by Category](results/profit_by_category.png)

**Business Insight**
- Business users can determine which product categories contribute the most profit and make better investment or assortment decisions.

### Customer Lifetime Value

This report estimates the long-term value of each customer based on their historical purchasing behavior. It is useful for prioritizing customer retention, loyalty programs, and high-value relationship management.

**Screenshot**

![Customer Lifetime Value](results/customer_lifetime_value.png)

**Business Insight**
- Business users can identify customers with the highest long-term potential and focus engagement strategies on preserving and growing those relationships.

### Repeat Customers

This report highlights customers who make multiple purchases over time. It helps teams understand loyalty, retention, and the effectiveness of repeat-buying behavior in the business.

**Screenshot**

![Repeat Customers](results/repeat_customers.png)

**Business Insight**
- Business users can understand customer retention patterns and identify opportunities to strengthen loyalty and recurring revenue.

### Average Order Value

This report measures the average amount spent per order. It is useful for understanding customer purchasing intensity and evaluating whether pricing, bundling, or upselling strategies are influencing spend size.

**Screenshot**

![Average Order Value](results/average_order_value.png)

**Business Insight**
- Business users can assess purchasing behavior at the order level and identify opportunities to increase revenue per transaction.

## SQL Analytics Reports

The project includes reporting logic for business-facing analytical questions. These reports help answer practical questions such as:

- Top Customers by Revenue: identifies the highest-value customers
- Revenue by Region: shows where revenue is concentrated geographically
- Revenue by Segment: highlights performance across customer segments
- Monthly Sales Trend: reveals sales movement over time
- Top Products: shows which products drive the most revenue
- Profit by Category: evaluates profitability by product category
- Customer Lifetime Value: estimates the long-term value of each customer
- Repeat Customers: identifies customers with multiple purchases
- Average Order Value: measures the average spending per order


## Key Features

- Automated ETL workflow from raw data to analytics-ready output
- Clean silver layer with validated data quality checks
- Gold layer built as a star schema for reporting
- Snowflake integration for warehouse-based storage and analysis
- Business-focused metrics for customer and sales analysis

