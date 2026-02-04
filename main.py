import subprocess
import os

from src.config.settings import Settings
from src.scripts.load_data import LoadData
from src.scripts.extract_data import ExtractData
from src.utils.move_product_catalog_to_dbt_seeds import MoveXlsxToSeeds

if __name__ == "__main__":
    settings = Settings()
    extract_data = ExtractData()
    load_data = LoadData()
    move_product_catalog = MoveXlsxToSeeds()
    move_product_catalog.read_google_sheets()
    move_product_catalog.load_csv_in_dbt_seeds()
    base_dir = settings.BASE_DIR
    os.chdir(os.path.join(base_dir, "products_scraping"))
    result = subprocess.run(["dbt", "seed"], capture_output=True, text=True)
    print(result.stdout)
    os.chdir(base_dir)
    load_data.create_scraping_error_logs_table()
    scraped_products = extract_data.extract()
    load_data.load(scraped_products)