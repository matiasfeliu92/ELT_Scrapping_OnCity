import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from src.config.settings import Settings
from src.config.logger import LoggerConfig

class MoveXlsxToSeeds:
    product_catalog_gsheet = None
    def __init__(self):
        self.settings = Settings()
        self.base_dir = self.settings.BASE_DIR
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.google_sheet_credentials = self.settings.GOOGLE_CREDENTIALS
        self.google_scopes = self.settings.GOOGLE_SCOPES
        self.product_catalog_csv_output = os.path.join(self.base_dir, "products_scraping", "seeds")

    def read_google_sheets(self): 
        try: 
            creds = Credentials.from_service_account_file( self.google_sheet_credentials, scopes=self.google_scopes ) 
            client = gspread.authorize(creds) 
            sheet_url = "https://docs.google.com/spreadsheets/d/1HWSNVwLffxLLnYf45-2QqF8br_qzkkzupd56h3RIMnU/edit"
            spreadsheet = client.open_by_url(sheet_url) 
            worksheet = spreadsheet.sheet1 
            data = worksheet.get_all_records() 
            self.product_catalog_gsheet = pd.DataFrame(data)
            self.logger.info("Product Catalog was load succesfully")
            return self.product_catalog_gsheet 
        except FileNotFoundError as e: 
            self.logger.error(f"Credenciales no encontradas: {e}") 
        except gspread.exceptions.SpreadsheetNotFound as e: 
            self.logger.error(f"No se encontró la hoja de cálculo: {e}") 
        except Exception as e: 
            self.logger.error(f"Error inesperado al leer Google Sheets: {e}") 
        return None
    
    def load_csv_in_dbt_seeds(self):
        if self.product_catalog_gsheet is not None:
            file_name = "product_catalog.csv"
            file_name_path = os.path.join(self.product_catalog_csv_output, file_name)
            self.product_catalog_gsheet.to_csv(file_name_path, sep=";", index=False)
            self.logger.info(f'Product Catalog was saved in CSV format ----- {file_name_path}')