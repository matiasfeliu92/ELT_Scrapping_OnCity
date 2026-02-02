from datetime import datetime, timedelta
import json
import platform
import pandas as pd
import os

from src.config.db import ManageDB
from src.config.logger import LoggerConfig
from src.scripts.load_data import LoadData
from src.scripts.scraping import Scraping
from src.config.scraping_settings import ScrapingSettings
from src.config.settings import Settings

class ExtractData:
    engine = None
    def __init__(self):
        self.db_config = ManageDB()
        self.settings = Settings()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.load_data = LoadData()
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

    def extract(self):
        query = f"""SELECT * FROM catalog.product_catalog"""
        product_links = pd.read_sql(query, con=self.engine)
        all_products_data = []
        output_json_path = self.settings.create_dir("data", "json")
        file_name = "all_products.json"
        json_complete_dir = os.path.join(output_json_path, file_name)
        if os.path.exists(json_complete_dir):
            last_update_ts = os.path.getmtime(json_complete_dir) 
            last_update = datetime.fromtimestamp(last_update_ts)
            if last_update.date() == datetime.now().date(): 
                print("El archivo está actualizado")
                with open(json_complete_dir, "r", encoding="utf-8") as f: 
                    all_products = json.load(f)
                    self.load_data.load(all_products)
            else: 
                print("El archivo está desactualizado")
                for _, row in product_links.iterrows():
                    scraped_at = datetime.now().strftime('%Y-%m-%d')
                    product_id = row["product_id"]
                    retailer = row["retailer"]
                    link = row["link"]
                    scraper = Scraping(link)
                    product_data = scraper.run()
                    print(product_data)
                    product_data_formatted = {
                        "scraped_at": scraped_at,
                        "product_id": product_id,
                        "retailer": retailer,
                        "data": product_data
                    }
                    all_products_data.append(product_data_formatted)
                with open(json_complete_dir, "w", encoding="utf-8") as f:
                    json.dump(all_products_data, f, ensure_ascii=False, indent=4)
                self.load_data.load(all_products_data)