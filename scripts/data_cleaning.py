"""
------------------------------------------------------------
Project : Customer Order Analytics
Script  : data_cleaning.py

Purpose:
Bronze -> Silver ETL Pipeline

Responsibilities:
1. Load raw customer order data (Bronze)
2. Standardize dataset
3. Clean text columns
4. Convert datatypes
5. Validate data quality
6. Save cleaned dataset (Silver)
------------------------------------------------------------
"""

import logging
from pathlib import Path

import pandas as pd


# ==========================================================
# Configuration
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_PATH = BASE_DIR / "data" / "bronze" / "SuperStoreOrders.csv"
SILVER_PATH = BASE_DIR / "data" / "silver" / "clean_superstore_orders.csv"


# ==========================================================
# Logging Configuration
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# Load Dataset
# ==========================================================

def load_data(file_path: Path) -> pd.DataFrame:
    """Load the Bronze dataset from disk."""

    logger.info("Loading Bronze dataset...")

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    df = pd.read_csv(file_path)

    logger.info(f"Rows Loaded    : {df.shape[0]}")
    logger.info(f"Columns Loaded : {df.shape[1]}")

    return df


# ==========================================================
# Standardize Column Names
# ==========================================================

def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names to lowercase snake_case."""

    logger.info("Standardizing column names...")

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    return df


# ==========================================================
# Clean Text Columns
# ==========================================================

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove leading and trailing whitespace from text columns."""

    logger.info("Cleaning text columns...")

    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    return df


# ==========================================================
# Convert Datatypes
# ==========================================================

def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert date and numeric columns to proper types."""

    logger.info("Converting datatypes...")

    df["order_date"] = (
        df["order_date"]
        .astype(str)
        .str.replace("-", "/", regex=False)
        .str.strip()
    )

    df["ship_date"] = (
        df["ship_date"]
        .astype(str)
        .str.replace("-", "/", regex=False)
        .str.strip()
    )

    df["order_date"] = pd.to_datetime(
        df["order_date"],
        format="%d/%m/%Y",
        errors="raise"
    )

    df["ship_date"] = pd.to_datetime(
        df["ship_date"],
        format="%d/%m/%Y",
        errors="raise"
    )

    df["sales"] = (
        df["sales"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    return df


# ==========================================================
# Data Validation
# ==========================================================

def validate_data(df: pd.DataFrame):
    """Validate the cleaned dataset before saving it."""

    logger.info("Running data validation...")

    missing_values = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    invalid_order_dates = df["order_date"].isna().sum()
    invalid_ship_dates = df["ship_date"].isna().sum()
    invalid_sales = df["sales"].isna().sum()
    negative_sales = (df["sales"] < 0).sum()
    negative_profit = (df["profit"] < 0).sum()
    negative_profit_pct = round((negative_profit / len(df)) * 100, 2)
    invalid_shipping = (df["ship_date"] < df["order_date"]).sum()

    if duplicate_rows > 0:
        raise ValueError(f"{duplicate_rows} duplicate rows found.")

    if invalid_order_dates > 0:
        raise ValueError(f"{invalid_order_dates} invalid order dates found.")

    if invalid_ship_dates > 0:
        raise ValueError(f"{invalid_ship_dates} invalid ship dates found.")

    if invalid_sales > 0:
        raise ValueError(f"{invalid_sales} invalid sales values found.")

    if negative_sales > 0:
        raise ValueError(f"{negative_sales} negative sales values found.")

    if invalid_shipping > 0:
        raise ValueError(
            f"{invalid_shipping} orders have ship date before order date."
        )

    logger.info("=" * 55)
    logger.info("Validation Summary")
    logger.info("=" * 55)
    logger.info(f"Rows Processed              : {len(df)}")
    logger.info(f"Missing Values             : {missing_values}")
    logger.info(f"Duplicate Rows             : {duplicate_rows}")
    logger.info(f"Invalid Order Dates        : {invalid_order_dates}")
    logger.info(f"Invalid Ship Dates         : {invalid_ship_dates}")
    logger.info(f"Invalid Sales Values       : {invalid_sales}")
    logger.info(f"Negative Sales             : {negative_sales}")
    logger.info(f"Negative Profit Records    : {negative_profit} ({negative_profit_pct}%)")
    logger.info(f"Invalid Shipping Records   : {invalid_shipping}")
    logger.info("=" * 55)
    logger.info("Validation completed successfully.")


# ==========================================================
# Save Silver Dataset
# ==========================================================

def save_data(df: pd.DataFrame, output_path: Path):
    """Save the cleaned dataset to the Silver layer."""

    logger.info("Saving Silver dataset...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    logger.info(f"Silver dataset saved successfully:\n{output_path}")


# ==========================================================
# Main Pipeline
# ==========================================================

def main():
    logger.info("=" * 60)
    logger.info("STARTING BRONZE -> SILVER ETL PIPELINE")
    logger.info("=" * 60)

    try:
        df = load_data(BRONZE_PATH)
        df = standardize_column_names(df)
        df = clean_text_columns(df)
        df = convert_data_types(df)
        validate_data(df)
        save_data(df, SILVER_PATH)

        logger.info("=" * 60)
        logger.info("BRONZE -> SILVER PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

    except Exception as error:
        logger.exception(f"Pipeline Failed : {error}")
        raise


if __name__ == "__main__":
    main()