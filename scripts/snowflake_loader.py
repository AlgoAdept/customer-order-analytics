import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DATA_DIR = BASE_DIR / "data"
GOLD_DIR = DATA_DIR / "gold"
SILVER_FILE = DATA_DIR / "silver" / "clean_superstore_orders.csv"
BRONZE_FILE = DATA_DIR / "bronze" / "SuperStoreOrders.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def get_connection() -> Any:
    logger.info("Connecting to Snowflake...")
    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD", "SNOWFLAKE_WAREHOUSE"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise ValueError("Missing Snowflake environment variables: " + ", ".join(missing))

    return snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE", "CUSTOMER_ORDER_ANALYTICS"),
        schema=os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )


def create_objects(conn: Any) -> None:
    db = os.getenv("SNOWFLAKE_DATABASE", "CUSTOMER_ORDER_ANALYTICS").upper()
    schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC").upper()
    logger.info("Creating Snowflake database and schema if missing...")
    for query in [f"CREATE DATABASE IF NOT EXISTS {db}", f"CREATE SCHEMA IF NOT EXISTS {db}.{schema}", f"USE DATABASE {db}", f"USE SCHEMA {db}.{schema}"]:
        conn.cursor().execute(query)


def create_tables(conn: Any) -> None:
    logger.info("Creating Snowflake tables if missing...")
    statements = [
        "CREATE OR REPLACE TABLE BRONZE_ORDERS (order_id STRING, order_date DATE, ship_date DATE, ship_mode STRING, customer_name STRING, segment STRING, state STRING, country STRING, market STRING, region STRING, product_id STRING, category STRING, sub_category STRING, product_name STRING, sales NUMBER(12,2), quantity NUMBER(10,0), discount NUMBER(6,4), profit NUMBER(12,2), shipping_cost NUMBER(12,2), order_priority STRING, year NUMBER(10,0))",
        "CREATE OR REPLACE TABLE SILVER_ORDERS (order_id STRING, order_date DATE, ship_date DATE, ship_mode STRING, customer_name STRING, segment STRING, state STRING, country STRING, market STRING, region STRING, product_id STRING, category STRING, sub_category STRING, product_name STRING, sales NUMBER(12,2), quantity NUMBER(10,0), discount NUMBER(6,4), profit NUMBER(12,2), shipping_cost NUMBER(12,2), order_priority STRING, year NUMBER(10,0))",
        "CREATE OR REPLACE TABLE DIM_CUSTOMER (customer_id NUMBER, customer_name STRING, segment STRING)",
        "CREATE OR REPLACE TABLE DIM_PRODUCT (product_id NUMBER, product_name STRING, category STRING, sub_category STRING)",
        "CREATE OR REPLACE TABLE DIM_LOCATION (location_id NUMBER, country STRING, state STRING, market STRING, region STRING)",
        "CREATE OR REPLACE TABLE DIM_DATE (date_id NUMBER, full_date DATE, year NUMBER, quarter NUMBER, month NUMBER, month_name STRING, day NUMBER, weekday STRING)",
        "CREATE OR REPLACE TABLE FACT_SALES (order_id STRING, customer_id NUMBER, product_id NUMBER, location_id NUMBER, date_id NUMBER, sales NUMBER(12,2), profit NUMBER(12,2), quantity NUMBER(10,0), discount NUMBER(6,4), shipping_cost NUMBER(12,2))",
        "CREATE OR REPLACE TABLE CUSTOMER_METRICS (customer_name STRING, segment STRING, market STRING, region STRING, country STRING, total_orders NUMBER, total_sales NUMBER(12,2), total_profit NUMBER(12,2), profit_margin_pct NUMBER(10,2), customer_lifetime_value NUMBER(12,2), total_quantity NUMBER, average_order_value NUMBER(12,2), average_discount NUMBER(10,4), first_order_date DATE, last_order_date DATE, customer_lifespan_days NUMBER, repeat_customer STRING)",
    ]
    for statement in statements:
        conn.cursor().execute(statement)


def load_csv_to_table(conn: Any, csv_path: Path, table_name: str) -> None:
    logger.info(f"Loading {csv_path.name} into {table_name}...")
    df = pd.read_csv(csv_path)
    if df.empty:
        logger.warning(f"No rows found in {csv_path.name}; skipping copy.")
        return

    schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC").upper()
    stage = f"@{os.getenv('SNOWFLAKE_DATABASE', 'CUSTOMER_ORDER_ANALYTICS').upper()}.{schema}.csv_stage_{table_name.lower()}"
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    cursor.execute(f"CREATE OR REPLACE STAGE {schema}.csv_stage_{table_name.lower()} FILE_FORMAT = (TYPE = CSV FIELD_OPTIONALLY_ENCLOSED_BY='\"' SKIP_HEADER = 1)")

    for col in ["order_date", "ship_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    for col in ["sales", "profit", "shipping_cost"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    if table_name == "CUSTOMER_METRICS":
        df = df[["customer_name", "segment", "market", "region", "country", "total_orders", "total_sales", "total_profit", "profit_margin_pct", "customer_lifetime_value", "total_quantity", "average_order_value", "average_discount", "first_order_date", "last_order_date", "customer_lifespan_days", "repeat_customer"]]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=str(BASE_DIR / "data")) as temp_file:
        df.to_csv(temp_file.name, index=False)
        temp_path = Path(temp_file.name)

    cursor.execute(f"PUT file://{temp_path.resolve()} {stage} AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
    cursor.execute(f"COPY INTO {table_name} FROM {stage}/{temp_path.name} FILE_FORMAT = (TYPE = CSV FIELD_OPTIONALLY_ENCLOSED_BY='\"' SKIP_HEADER = 1)")
    cursor.execute(f"REMOVE {stage}/{temp_path.name}")
    temp_path.unlink(missing_ok=True)

    loaded = int(conn.cursor().execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])
    logger.info(f"Loaded {loaded} rows into {table_name}")


def main() -> None:
    try:
        logger.info("STARTING SNOWFLAKE LOAD PROCESS")
        conn = get_connection()
        create_objects(conn)
        create_tables(conn)
        load_csv_to_table(conn, BRONZE_FILE, "BRONZE_ORDERS")
        load_csv_to_table(conn, SILVER_FILE, "SILVER_ORDERS")
        for csv_path, table_name in [(GOLD_DIR / "dim_customer.csv", "DIM_CUSTOMER"), (GOLD_DIR / "dim_product.csv", "DIM_PRODUCT"), (GOLD_DIR / "dim_location.csv", "DIM_LOCATION"), (GOLD_DIR / "dim_date.csv", "DIM_DATE"), (GOLD_DIR / "fact_sales.csv", "FACT_SALES"), (GOLD_DIR / "customer_metrics.csv", "CUSTOMER_METRICS")]:
            if not csv_path.exists():
                raise FileNotFoundError(f"Missing Gold file: {csv_path}")
            load_csv_to_table(conn, csv_path, table_name)
        logger.info("SNOWFLAKE LOAD COMPLETED SUCCESSFULLY")
    except Exception as error:
        logger.exception(f"Snowflake load failed: {error}")
        raise


if __name__ == "__main__":
    main()
