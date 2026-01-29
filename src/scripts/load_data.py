from datetime import datetime
import json
import platform
from typing import List

import pandas as pd
from sqlalchemy import JSON, Column, MetaData, Table, func, inspect, select, TIMESTAMP, VARCHAR
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
        table_name = "raw_products_scraping"
        metadata = MetaData()
        raw_products_scraping = Table(
            table_name,
            metadata,
            Column("date", TIMESTAMP),
            Column("link", VARCHAR),
            Column("data", JSON),
        )
        last_ts = self.get_last_timestamp.execute(self.engine, raw_products_scraping)
        if last_ts:
            self.logger.info(f"Tabla detectada. Último registro procesado: {last_ts}")
        else:
            self.logger.info(f"Tabla no existe o está vacía. Se realizará carga total.")
            metadata.create_all(self.engine)
        self.logger.info(f"Insertando {len(__data__)} registros nuevos.")
        now = datetime.now() 
        formatted_data = [] 
        for obj in __data__: 
            formatted_data.append({ 
                "date": now,
                "link": obj.get("link", ""), # fallback si no hay link 
                "data": obj 
            })
        with self.engine.begin() as conn:
            conn.execute(raw_products_scraping.insert(), formatted_data)
            self.logger.info(f"Data successfully loaded into table: {table_name}")
        self.logger.info("Data load process completed.")