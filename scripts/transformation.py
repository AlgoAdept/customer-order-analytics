import logging
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
SILVER_FILE = BASE_DIR / "data" / "silver" / "clean_superstore_orders.csv"
GOLD_DIR = BASE_DIR / "data" / "gold"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def load_data() -> pd.DataFrame:
    logger.info("Loading Silver dataset...")
    df = pd.read_csv(SILVER_FILE, parse_dates=["order_date", "ship_date"])
    logger.info(f"Rows Loaded : {len(df)}")
    return df


def build_surrogate_key(values: pd.Series) -> pd.Series:
    codes, _ = pd.factorize(values.astype(str).str.strip(), sort=True)
    return pd.Series(codes + 1, index=values.index, dtype="int64")


def create_dim_customer(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Creating customer dimension...")
    dim = df[["customer_name", "segment"]].drop_duplicates().reset_index(drop=True)
    dim["customer_id"] = build_surrogate_key(dim["customer_name"] + "|" + dim["segment"])
    return dim[["customer_id", "customer_name", "segment"]]


def create_dim_product(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Creating product dimension...")
    dim = df[["product_id", "product_name", "category", "sub_category"]].drop_duplicates(subset=["product_id"]).reset_index(drop=True)
    dim["product_business_key"] = dim["product_id"].astype(str).str.strip()
    dim["product_id"] = build_surrogate_key(dim["product_business_key"])
    return dim[["product_id", "product_name", "category", "sub_category", "product_business_key"]]


def create_dim_location(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Creating location dimension...")
    dim = df[["country", "state", "market", "region"]].drop_duplicates().reset_index(drop=True)
    dim["location_business_key"] = dim["country"].astype(str).str.strip() + "|" + dim["state"].astype(str).str.strip() + "|" + dim["market"].astype(str).str.strip() + "|" + dim["region"].astype(str).str.strip()
    dim["location_id"] = build_surrogate_key(dim["location_business_key"])
    return dim[["location_id", "country", "state", "market", "region", "location_business_key"]]


def create_dim_date(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Creating date dimension...")
    dates = pd.DataFrame({"full_date": pd.Series(df["order_date"].dropna().sort_values().unique())})
    dates["date_id"] = dates["full_date"].dt.strftime("%Y%m%d").astype(int)
    dates["year"] = dates["full_date"].dt.year
    dates["quarter"] = dates["full_date"].dt.quarter
    dates["month"] = dates["full_date"].dt.month
    dates["month_name"] = dates["full_date"].dt.strftime("%B")
    dates["day"] = dates["full_date"].dt.day
    dates["weekday"] = dates["full_date"].dt.day_name()
    return dates[["date_id", "full_date", "year", "quarter", "month", "month_name", "day", "weekday"]]


def create_fact_sales(df: pd.DataFrame, dim_customer: pd.DataFrame, dim_product: pd.DataFrame, dim_location: pd.DataFrame, dim_date: pd.DataFrame) -> pd.DataFrame:
    logger.info("Creating fact sales table...")
    fact = df[["order_id", "order_date", "customer_name", "segment", "product_id", "country", "state", "market", "region", "sales", "profit", "quantity", "discount", "shipping_cost"]].copy()
    fact = fact.merge(dim_customer[["customer_id", "customer_name", "segment"]], on=["customer_name", "segment"], how="left")
    fact = fact.rename(columns={"product_id": "product_business_key"}).merge(dim_product[["product_id", "product_business_key"]], on="product_business_key", how="left").drop(columns=["product_business_key"])
    fact = fact.merge(dim_location[["location_id", "country", "state", "market", "region"]], on=["country", "state", "market", "region"], how="left")
    fact = fact.merge(dim_date[["date_id", "full_date"]], left_on="order_date", right_on="full_date", how="left").drop(columns=["full_date", "customer_name", "segment", "country", "state", "market", "region", "order_date"])
    fact = fact[["order_id", "customer_id", "product_id", "location_id", "date_id", "sales", "profit", "quantity", "discount", "shipping_cost"]]
    if fact[["customer_id", "product_id", "location_id", "date_id"]].isna().any().any():
        raise ValueError("One or more surrogate keys could not be resolved in fact_sales.")
    return fact


def create_customer_metrics(fact_sales: pd.DataFrame, dim_customer: pd.DataFrame, dim_location: pd.DataFrame, dim_date: pd.DataFrame) -> pd.DataFrame:
    logger.info("Generating customer metrics from the star schema...")
    metrics = (
        fact_sales.merge(dim_customer[["customer_id", "customer_name", "segment"]], on="customer_id", how="left")
        .merge(dim_location[["location_id", "market", "region", "country"]], on="location_id", how="left")
        .merge(dim_date[["date_id", "full_date"]], on="date_id", how="left")
    )
    metrics = metrics.groupby(["customer_name", "segment", "market", "region", "country"], as_index=False).agg(
        total_orders=("order_id", "nunique"),
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
        average_order_value=("sales", "mean"),
        average_discount=("discount", "mean"),
        first_order_date=("full_date", "min"),
        last_order_date=("full_date", "max"),
    )
    metrics["profit_margin_pct"] = np.where(metrics["total_sales"] != 0, (metrics["total_profit"] / metrics["total_sales"]) * 100, 0).round(2)
    metrics["customer_lifetime_value"] = metrics["total_profit"].round(2)
    metrics["customer_lifespan_days"] = (metrics["last_order_date"] - metrics["first_order_date"]).dt.days
    metrics["repeat_customer"] = np.where(metrics["total_orders"] > 1, "Yes", "No")
    metrics["average_order_value"] = metrics["average_order_value"].round(2)
    metrics["average_discount"] = metrics["average_discount"].round(4)
    metrics["total_sales"] = metrics["total_sales"].round(2)
    metrics["total_profit"] = metrics["total_profit"].round(2)
    return metrics[["customer_name", "segment", "market", "region", "country", "total_orders", "total_sales", "total_profit", "profit_margin_pct", "customer_lifetime_value", "total_quantity", "average_order_value", "average_discount", "first_order_date", "last_order_date", "customer_lifespan_days", "repeat_customer"]].sort_values(by="total_sales", ascending=False)


def validate_output(df: pd.DataFrame, label: str):
    logger.info(f"Running validation for {label}...")
    logger.info(f"Rows in {label} : {len(df)}")
    if df.empty:
        raise ValueError(f"{label} is empty.")


def save_outputs(outputs: dict[str, pd.DataFrame]):
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in outputs.items():
        file_path = GOLD_DIR / f"{name}.csv"
        df.to_csv(file_path, index=False, date_format="%Y-%m-%d")
        logger.info(f"Saved {name} -> {file_path}")


def main():
    try:
        logger.info("=" * 60)
        logger.info("STARTING SILVER -> GOLD TRANSFORMATION")
        logger.info("=" * 60)
        df = load_data()
        dim_customer = create_dim_customer(df)
        dim_product = create_dim_product(df)
        dim_location = create_dim_location(df)
        dim_date = create_dim_date(df)
        fact_sales = create_fact_sales(df, dim_customer, dim_product, dim_location, dim_date)
        customer_metrics = create_customer_metrics(fact_sales, dim_customer, dim_location, dim_date)
        for label, current in [("dim_customer", dim_customer), ("dim_product", dim_product), ("dim_location", dim_location), ("dim_date", dim_date), ("fact_sales", fact_sales), ("customer_metrics", customer_metrics)]:
            validate_output(current, label)
        save_outputs({"dim_customer": dim_customer[["customer_id", "customer_name", "segment"]], "dim_product": dim_product[["product_id", "product_name", "category", "sub_category"]], "dim_location": dim_location[["location_id", "country", "state", "market", "region"]], "dim_date": dim_date, "fact_sales": fact_sales, "customer_metrics": customer_metrics})
        logger.info("=" * 60)
        logger.info("GOLD LAYER CREATED SUCCESSFULLY")
        logger.info("=" * 60)
    except Exception:
        logger.exception("Pipeline Failed")
        raise


if __name__ == "__main__":
    main()