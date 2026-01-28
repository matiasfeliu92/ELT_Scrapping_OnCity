import pandas as pd
import os

from src.scripts.scraping import Scraping
from src.config.scraping_settings import ScrapingSettings

scraping_settings = ScrapingSettings()

if __name__ == "__main__":
    products_links_dir = os.path.join(scraping_settings.INPUTS_DIR, "product_links_for_ELT_scraping.csv")
    links = pd.read_csv(products_links_dir, sep=";")
    for _, row in links[0:5].iterrows():
        # if "megatone.net" not in row["link"]:
        # if "fravega.com" not in row["link"]:
        # if "musimundo.com" not in row["link"]:
        # if "naldo.com.ar" not in row["link"]:
        #     continue
        link = row["link"]
        scraper = Scraping(link)
        product_data = scraper.run()
        print(product_data)