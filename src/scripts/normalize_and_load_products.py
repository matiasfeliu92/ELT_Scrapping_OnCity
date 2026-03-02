import json

import pandas as pd
from sqlalchemy.sql import over
from sqlalchemy import Column, Float, Integer, String, select, func, desc, Table, MetaData

from src.config.db import ManageDB
from src.config.logger import LoggerConfig
from src.config.settings import Settings
from src.utils.normalize_price import NormalizePrice

class NormalizeAndLoadScrapedProducts:
    engine = None
    def __init__(self):
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.config_db = ManageDB()
        self.normalize_price = NormalizePrice()
        self.settings = Settings()
        self.products_scraping_schema = "raw"
        self.products_scraping_table = "scraping_data"
        self.product_catalog_schema = "catalog"
        self.product_catalog_table = "product_catalog"
        self.scraped_products_df = pd.DataFrame()  # Inicializa el DataFrame para almacenar los productos
        self.products_table = "products"

    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Transforming data...")
        self.logger.info(f"COLUMNS IN DATA TO NORMALIZE: {df.columns}")
        df["scraped_list_price"] = df["scraped_list_price"].apply(self.normalize_price.execute)
        df["scraped_cash_price"] = df["scraped_cash_price"].apply(self.normalize_price.execute)

        df["is_active"] = (
            (df["scraped_cash_price"].notna() |
            df["scraped_list_price"].notna()) &
            (df["scraped_name"].notnull() | df["scraped_sku"].notnull())
        )

        df.rename(columns={
            "scraped_sku": "sku",
            "scraped_name": "name",
            "scraped_main_category": "main_category_scraped",
            "scraped_sub_category": "sub_category_scraped",
            "scraped_stock": "stock",
            "scraped_store": "store"
        }, inplace=True)

        return df

    def read_data(self):
        self.logger.info("Reading data from the database...")
        self.engine = self.config_db.create_engine(
            self.settings.POSTGRES_CONNECTION_STRING_NEW_DB
        )
        metadata = MetaData()
        scraping_table = Table(
            self.products_scraping_table,
            metadata,
            schema=self.products_scraping_schema,
            autoload_with=self.engine
        )
        catalog_table = Table(
            self.product_catalog_table,
            metadata,
            schema=self.product_catalog_schema,
            autoload_with=self.engine
        )
        product_table = Table(
            "products",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("sku", String),
            Column("name", String),
            Column("list_price", Float),
            Column("cash_price", Float),
            Column("stock", String),
            Column("store", String),
            schema="raw"
        )
        metadata.create_all(self.engine)
        row_number_column = func.row_number().over(
            partition_by=[
                scraping_table.c.product_id,
                scraping_table.c.retailer
            ],
            order_by=scraping_table.c.scraped_at.desc()
        ).label("rn")
        ranked_subquery = (
            select(
                catalog_table.c.product_id,
                catalog_table.c.brand,
                catalog_table.c.model,
                catalog_table.c.main_category,
                catalog_table.c.sub_category,
                catalog_table.c.retailer,
                catalog_table.c.link,
                scraping_table.c.scraped_at.label("updated_at"),
                scraping_table.c.raw_data["sku"].astext.label("scraped_sku"),
                scraping_table.c.raw_data["name"].astext.label("scraped_name"),
                scraping_table.c.raw_data["main_category"].astext.label("scraped_main_category"),
                scraping_table.c.raw_data["sub_category"].astext.label("scraped_sub_category"),
                scraping_table.c.raw_data["list_price"].astext.label("scraped_list_price"),
                scraping_table.c.raw_data["cash_price"].astext.label("scraped_cash_price"),
                scraping_table.c.raw_data["stock"].astext.label("scraped_stock"),
                scraping_table.c.raw_data["store"].astext.label("scraped_store"),
                row_number_column
            )
            .join(
                catalog_table,
                (scraping_table.c.product_id == catalog_table.c.product_id) &
                (scraping_table.c.retailer == catalog_table.c.retailer)
            )
        ).subquery()
        final_query = (
            select(ranked_subquery)
            .where(ranked_subquery.c.rn == 1)
            .order_by(func.right(ranked_subquery.c.product_id, 3))
        )
        try:
            self.logger.info(f"Executing query:\n{final_query}")
            self.scraped_products_df = pd.read_sql(final_query, self.engine)
            self.logger.info(
                f"Data read successfully. Number of records: {len(self.scraped_products_df)}"
            )
            scraped_products_df_V2  = self.normalize_data(self.scraped_products_df)
            scraped_products_df_V2.to_sql(product_table.name, con=self.engine, schema=product_table.schema, if_exists="replace", index=False)
        except Exception as e:
            self.logger.error(f"Error reading data: {e}")


if __name__ == "__main__":
    normalize_and_load = NormalizeAndLoadScrapedProducts()
    scraped_products = normalize_and_load.read_data()