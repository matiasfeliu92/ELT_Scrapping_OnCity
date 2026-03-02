from datetime import datetime, timedelta
import json
import platform
import pandas as pd
import os

from sqlalchemy import MetaData, Table

from src.config.db import ManageDB
from src.config.logger import LoggerConfig
from src.scripts.load_data import LoadData
from src.scripts.scraping import Scraping
from src.config.settings import Settings
from src.utils.get_last_timestamp import GetLastTimestamp

class ExtractData:
    engine = None
    def __init__(self):
        self.db_config = ManageDB()
        self.settings = Settings()
        self.load_data = LoadData()
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
        self.engine = self.db_config.create_engine(self.conn_string_new_DB)
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.all_products_data = []

    def extract(self):
        product_catalog_query = f"""SELECT * FROM catalog.product_catalog"""
        product_catalog_links = pd.read_sql(product_catalog_query, con=self.engine)
        self.logger.info("scraping_data table wasn't updated")
        self.logger.info("Scraping process will start now")
        for _, row in product_catalog_links.sample(5).iterrows():
            scraped_at = datetime.now().strftime('%Y-%m-%d')
            product_id = row["product_id"]
            retailer = row["retailer"]
            link = row["link"]
            scraper = Scraping(link, product_id, retailer)
            product_data = scraper.run()
            print(product_data)
            product_data_formatted = {
                "scraped_at": scraped_at,
                "product_id": product_id,
                "retailer": retailer,
                "data": product_data
            }
            self.logger.info("Scraping process run successfuly")
            self.load_data = LoadData()
            self.load_data.load(product_data_formatted)