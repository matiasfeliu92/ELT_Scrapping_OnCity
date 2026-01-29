from datetime import datetime, timedelta
import json
import pandas as pd
import os

from src.scripts.load_data import LoadData
from src.scripts.scraping import Scraping
from src.config.scraping_settings import ScrapingSettings
from src.config.settings import Settings

scraping_settings = ScrapingSettings()
settings = Settings()

if __name__ == "__main__":
    products_links_dir = os.path.join(scraping_settings.INPUTS_DIR, "product_links_for_ELT_scraping.csv")
    links = pd.read_csv(products_links_dir, sep=";")
    all_products_data = []
    output_json_path = settings.create_dir("data", "json")
    file_name = "all_products.json"
    json_complete_dir = os.path.join(output_json_path, file_name)
    load_data = LoadData()
    if os.path.exists(json_complete_dir):
        last_update_ts = os.path.getmtime(json_complete_dir)
        last_update = datetime.fromtimestamp(last_update_ts)
        if datetime.now() - last_update < timedelta(hours=24): 
            print("El archivo está actualizado")
            with open(json_complete_dir, "r", encoding="utf-8") as f: 
                all_products = json.load(f)
                load_data.load(all_products)
        else: 
            print("El archivo está desactualizado")
            for _, row in links.iterrows():
                link = row["link"]
                scraper = Scraping(link)
                product_data = scraper.run()
                print(product_data)
                all_products_data.append(product_data)
            with open(json_complete_dir, "w", encoding="utf-8") as f:
                json.dump(all_products_data, f, ensure_ascii=False, indent=4)