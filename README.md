# Customer Order Analytics

## Project Overview

Customer Order Analytics is an ETL-based Data Engineering project that analyzes customer purchasing behavior using a global retail dataset. The project follows a simplified Medallion Architecture (Bronze → Silver → Gold) to organize raw, cleaned, and business-ready data.

The final output is loaded into Snowflake, where SQL queries generate business reports and customer insights.

---

## Project Objectives

- Build an end-to-end ETL pipeline.
- Clean and validate raw customer order data.
- Generate customer-level business metrics.
- Load processed datasets into Snowflake.
- Create SQL reports for business analysis.
- Track project progress using Git and GitHub.

---

## Architecture

```
                 ETL Pipeline

      Bronze (Raw CSV)
              │
              ▼
      Silver (Clean Data)
              │
              ▼
   Gold (Customer Metrics)
              │
              ▼
        Snowflake Warehouse
              │
              ▼
        SQL Business Reports
```

---

## Project Structure

```
Customer-Order-Analytics/

│
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── notebooks/
│
├── scripts/
│   ├── data_cleaning.py
│
├── sql/
│
├── requirements.txt
│
└── README.md
```

---

## Technologies Used

- Python
- Pandas
- Jupyter Notebook
- Snowflake
- SQL
- Git
- GitHub

---

# Project Progress

## ✅ Phase 1 : Project Setup

- Created project structure
- Initialized Git repository
- Connected GitHub repository
- Configured virtual environment

---

## ✅ Phase 2 : Data Profiling

Completed exploratory profiling of the raw dataset.

Performed:

- Dataset overview
- Missing value analysis
- Duplicate detection
- Datatype analysis
- Numerical summary
- Customer statistics
- Order statistics
- Date range analysis
- Region distribution
- Top customers

---

## ✅ Phase 3 : Data Cleaning (Bronze → Silver)

Implemented a production-style ETL pipeline.

Cleaning Steps

- Standardized column names
- Trimmed text columns
- Standardized mixed date separators
- Converted date columns
- Converted sales datatype
- Validated duplicate rows
- Validated missing values
- Validated shipping dates
- Preserved valid negative profit records
- Saved cleaned dataset to Silver layer

---

## Upcoming Work

- Gold Layer Transformation
- Customer Lifetime Value (CLV)
- Average Order Value (AOV)
- Repeat Customer Identification
- Load to Snowflake
- SQL Reports