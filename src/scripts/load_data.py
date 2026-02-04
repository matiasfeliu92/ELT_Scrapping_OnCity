from datetime import datetime
import json
import platform
from typing import List

import pandas as pd
from sqlalchemy import Column, DateTime, MetaData, String, Table, INTEGER, UniqueConstraint, inspect, schema
from sqlalchemy.dialects.postgresql import JSONB, insert
from src.config.settings import Settings
from src.config.logger import LoggerConfig
from src.config.db import ManageDB
from src.utils.get_last_timestamp import GetLastTimestamp


class LoadData:
    def __init__(self):
        self.db_config = ManageDB()
        self.settings = Settings()
        self.get_last_timestamp = GetLastTimestamp()
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
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    def load(self, __data__: List[dict]):
        if not __data__: 
            self.logger.warning("No hay datos para insertar, se omite la carga.") 
            return        
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
            inspector = inspect(conn)
            if "raw" not in inspector.get_schema_names():
                conn.execute(schema.CreateSchema("raw"))
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
            stmt = insert(raw_products_scraping).values(formatted_rows)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["scraped_at", "product_id", "retailer"]
            )
            with self.engine.begin() as conn:
                conn.execute(stmt)
            self.logger.info(
                f"Data successfully loaded into table: raw.{table_name} (duplicates ignored)"
            )

        self.logger.info("Data load process completed.")

    def create_scraping_error_logs_table(self):
        scraping_error_logs_table_query = f""" 
            CREATE TABLE IF NOT EXISTS logs.scraping_error_logs ( 
                id SERIAL PRIMARY KEY, 
                log_time DATE NOT NULL, 
                product_id VARCHAR(100), 
                retailer VARCHAR(100), 
                field VARCHAR(100),
                error JSONB NOT NULL,
                CONSTRAINT uq_scraping_error UNIQUE (log_time, product_id, retailer, field)
            ); 
        """ 
        conn = self.db_config.create_connection(self.conn_string_for_cursor_default_DB)
        self.db_config.create_database(conn, self.settings.POSTGRES_DB_NAME_USE)
        conn_new_db = self.db_config.create_connection(self.conn_string_for_cursor_new_DB)
        self.db_config.create_schema(conn_new_db, "logs")
        cursor_new_db = conn_new_db.cursor()
        cursor_new_db.execute(scraping_error_logs_table_query)
        conn_new_db.commit()

    def create_logs_table(self):
        pass

    def load_scraping_error_logs(self, product_id, retailer, exception, message, by, path, field):
        self.engine = self.db_config.create_engine(self.conn_string_new_DB)
        metadata = MetaData(schema="logs") 
        scraping_error_logs = Table("scraping_error_logs", metadata, autoload_with=self.engine)
        error_entry = { 
            "log_time": datetime.now().date(), 
            "product_id": product_id, 
            "retailer": retailer, 
            "field": field,
            "error": { 
                "exception": exception, 
                "message": message, 
                "by": by, 
                "path": path 
            } 
        }
        with self.engine.begin() as conn: 
            stmt = insert(scraping_error_logs).values(error_entry) 
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["log_time", "product_id", "retailer", "field"]
            )
            conn.execute(stmt)