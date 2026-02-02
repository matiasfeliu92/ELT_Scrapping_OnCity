from datetime import datetime
import json
import platform
from typing import List

import pandas as pd
from sqlalchemy import Column, DateTime, MetaData, String, Table, INTEGER, UniqueConstraint, schema
from sqlalchemy.dialects.postgresql import JSONB
from src.config.settings import Settings
from src.config.logger import LoggerConfig
from src.config.db import ManageDB
from src.utils.get_last_timestamp import GetLastTimestamp


class LoadData:
    def __init__(self):
        self.db_config = ManageDB()
        self.settings = Settings()
        self.get_last_timestamp = GetLastTimestamp()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.conn_string_default_DB = (
            self.settings.POSTGRES_CONNECTION_STRING_DEFAULT_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CONNECTION_STRING_DOCKER_DEFAULT_DB
        )
        self.conn_string_for_cursor_default_DB = (
            self.settings.POSTGRES_CURSOR_CONNECTION_STRING_DEFAULT_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CURSOR_CONNECTION_STRING_DOCKER_DEFAULT_DB
        )
        self.engine = None
        self.conn_string_new_DB = (
            self.settings.POSTGRES_CONNECTION_STRING_NEW_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CONNECTION_STRING_DOCKER_NEW_DB
        )
        self.conn_string_for_cursor_new_DB = (
            self.settings.POSTGRES_CURSOR_CONNECTION_STRING_NEW_DB
            if platform.system() == "Windows"
            else self.settings.POSTGRES_CURSOR_CONNECTION_STRING_DOCKER_NEW_DB
        )

    def load(self, __data__: List[dict]):
        self.logger.info(f"SYSTEM PLATFORM: {platform.system()}")
        self.logger.info("Starting database connection and setup...")
        self.engine = self.db_config.create_engine(self.conn_string_default_DB)
        conn = self.db_config.create_connection(self.conn_string_for_cursor_default_DB)
        self.db_config.create_database(conn, self.settings.POSTGRES_DB_NAME_USE)
        conn.close()
        self.engine = self.db_config.create_engine(self.conn_string_new_DB)
        self.logger.info("Database and schema setup completed.")
        self.logger.info("Starting data load into database...")
        table_name = "scraping_data"
        metadata = MetaData(schema="raw")
        raw_products_scraping = Table(
            table_name,
            metadata,
            Column("id", INTEGER, primary_key=True, autoincrement=True), # Recomendado para tracking
            Column("scraped_at", DateTime),
            Column("product_id", String),
            Column("retailer", String),
            Column("raw_data", JSONB),      # El dump completo del scraper
            UniqueConstraint("scraped_at", "product_id", "retailer", name="uq_scraped_product_retailer")
        )
        with self.engine.begin() as conn:
            conn.execute(schema.CreateSchema("raw", if_not_exists=True))
            metadata.create_all(conn)
        self.logger.info(f"Insertando {len(__data__)} registros nuevos.")
        formatted_rows = []
        for item in __data__:
            formatted_rows.append({
                "scraped_at": item.get("scraped_at", datetime.now()),
                "product_id": item.get("product_id"),
                "retailer": item.get("retailer"),
                "raw_data": item.get("data")
            })
        with self.engine.begin() as conn:
            conn.execute(raw_products_scraping.insert(), formatted_rows)
            self.logger.info(f"Data successfully loaded into table: raw.{table_name}")

        self.logger.info("Data load process completed.")