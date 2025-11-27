import os
import random
import sys
import time
import pandas as pd
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

args = sys.argv[1:]
logging.info({"PARAMETROS": args})


class Scrap:
    def __init__(self):
        self.i = args[0]
        self.base_url = "https://www.oncity.com"
        self.endpoints = [
            "/tecnologia?page={}",
            "/electrodomesticos?page={}",
            "/deportes-y-fitness?page={}",
            "/audio-tv-y-video?page={}",
            "/belleza-y-cuidado-personal?page={}",
        ]
        self.base_dir = os.getcwd()
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"user-agent={self.USER_AGENT}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.errors_extracting = []
        self.products_links = []
        self.all_products_data = []

    def safe_find_elements(
        self, by, path, multiple=False, index=0, default="", timeout=10
    ):
        try:
            wait = WebDriverWait(self.driver, timeout)
            if multiple:
                print("MULTIPLE")
                wait.until(EC.presence_of_all_elements_located((by, path)))
                elements = self.driver.find_elements(by, path)
                return elements if elements else []
            else:
                print("ELEMENT")
                wait.until(EC.presence_of_element_located((by, path)))
                element = self.driver.find_element(by, path)
                return element if element else None
        except Exception as e:
            print("Fallo al obtener el texto:", e)
            return default

    def extract_links(self):
        i = 1
        while i < int(self.i):
            for path in self.endpoints:
                try:
                    complete_url = f"{self.base_url}{path.format(i)}"
                    logging.info(f"ACCEDIENDO A {complete_url}")
                    self.driver.get(complete_url)
                    time.sleep(random.uniform(2, 5))
                    main_products_container = self.safe_find_elements(
                        By.ID, "gallery-layout-container"
                    )
                    product_cards = main_products_container.find_elements(
                        By.CSS_SELECTOR, 'div[data-af-element="search-result"]'
                    )
                    for card in product_cards:
                        name = card.find_element(
                            By.CLASS_NAME,
                            "vtex-product-summary-2-x-productNameContainer",
                        )
                        link = card.find_element(By.TAG_NAME, "a")
                        logging.info(
                            {
                                "name": name.text,
                                "link": link.get_attribute("href"),
                            }
                        )
                        self.products_links.append(
                            {
                                "name": name.text,
                                "link": link.get_attribute("href"),
                            }
                        )
                except Exception as e:
                    logging.error(
                        f"Error: {str(e)}\nURL: {self.base_url}{path.format(i)}"
                    )
            i += 1
        products_links = pd.DataFrame(self.products_links)
        products_links_final = products_links.drop_duplicates(subset=["name"])
        os.makedirs(os.path.join(self.base_dir, "data", "input"), exist_ok=True)
        output_dir = os.path.join(self.base_dir, "data", "input")
        logging.info(output_dir)
        products_links_final.to_csv(
            os.path.join(output_dir, "products_to_scrap.csv"),
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )

    def extract_data(self):
        input_dir = os.path.join(self.base_dir, "data", "input")
        path_input_links = os.path.join(input_dir, "products_to_scrap.csv")
        input_links = pd.read_csv(path_input_links, sep=";")
        logging.info(input_links.head())
        for index, row in input_links.iterrows():
            logging.info(
                "---------------------------------------------------------------------------------------------------"
            )
            product_data = {}
            name = row["name"]
            link = row["link"]
            logging.info(f"ACCEDIENDO A {link}")
            self.driver.get(link)
            time.sleep(random.uniform(2, 5))
            category_path = self.safe_find_elements(
                By.CSS_SELECTOR, 'div[data-testid="breadcrumb"]'
            )
            category_path_elements = category_path.find_elements(By.TAG_NAME, "a")
            promo = self.safe_find_elements(
                By.CSS_SELECTOR,
                'span[class="vtex-product-highlights-2-x-productHighlightText"]',
            )
            if promo:
                logging.info(f"----------------PROMO----------------: {promo.text}")
                product_data["promo"] = promo.text
            else:
                logging.warning("NO AVAILABLE PROMO")
            sku = self.safe_find_elements(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[3]/div/div/div[2]/div/div[3]/div",
            )
            if sku:
                logging.info(f"----------------SKU----------------: {sku.text}")
                product_data["sku"] = sku.text
            else:
                logging.warning("INVALID SKU")
            price_with_discount = self.safe_find_elements(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[3]/div/div/div[2]/div/div[6]/div/div/div/div/div[1]/div/div/div[1]/span/span/span",
            )
            if price_with_discount:
                logging.info(
                    f"----------------PRICE WITH DISCOUNT----------------: {price_with_discount.text}"
                )
                product_data["price_with_discount"] = price_with_discount.text
            else:
                logging.warning("INVALID PRICE WITH DISCOUNT")
            discount_applicated = self.safe_find_elements(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[3]/div/div/div[2]/div/div[6]/div/div/div/div/div[1]/div/div/div[2]/span",
            )
            if discount_applicated:
                logging.info(
                    f"----------------DISCOUNT APPLICATED----------------: {discount_applicated.text}"
                )
                product_data["discount_applicated"] = discount_applicated.text
            else:
                logging.warning("NO DISCOUNT APPLICATED")
            original_price = self.safe_find_elements(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[3]/div/div/div[2]/div/div[6]/div/div/div/div/div[2]/div/div/div/span/span/span",
            )
            if original_price:
                logging.info(
                    f"----------------ORIGINAL PRICE----------------: {original_price.text}"
                )
                product_data["original_price"] = original_price.text
            else:
                logging.warning("INVALID PRICE")
            brand = self.safe_find_elements(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[3]/div/div/div[2]/div/div[17]/div/div/div/div/div[2]/div/div[1]/div/div[1]/span[2]",
            )
            if brand:
                logging.info(f"----------------BRAND----------------: {brand.text}")
                product_data["brand"] = brand.text
            else:
                logging.warning("INVALID BRAND")
            origin = self.safe_find_elements(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[3]/div/div/div[2]/div/div[17]/div/div/div/div/div[2]/div/div[1]/div/div[3]/span[2]",
            )
            if origin:
                logging.info(f"----------------ORIGIN----------------: {origin.text}")
                product_data["origin"] = origin.text
            else:
                logging.warning("INVALID ORIGIN")
            warranty = self.safe_find_elements(
                By.XPATH,
                "/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[3]/div/div/div[2]/div/div[17]/div/div/div/div/div[2]/div/div[1]/div/div[4]/span[2]",
            )
            if warranty:
                logging.info(
                    f"----------------WARRANTY----------------: {warranty.text}"
                )
                product_data["warranty"] = warranty.text
            else:
                logging.warning("INVALID WARRANTY")
            stars_count = self.safe_find_elements(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[7]/div/div/section/section[1]/div[1]/section[1]/section/div/div[1]/div/div[2]')
            if stars_count:
                logging.info(
                    f"----------------STARS COUNT----------------: {stars_count.text}"
                )
                product_data["stars_count"] = stars_count.text
            else:
                logging.warning("NO STARS COUNT")
            opinions = self.safe_find_elements(By.XPATH, '/html/body/div[2]/div/div[1]/div/div/div/div[2]/div/div[2]/div[1]/section/div/div[7]/div/div/section/section[1]/div[1]/section[1]/section/div/div[2]/span')
            if opinions:
                logging.info(
                    f"----------------OPINIONS----------------: {opinions.text}"
                )
                product_data["opinions"] = opinions.text
            else:
                logging.warning("NO OPINIONS")
            product_data["name"] = name
            product_data["link"] = link
            num_categories = len(category_path_elements)
            product_data["main_category"] = (
                category_path_elements[1].text if num_categories > 1 else "Unknown"
            )
            product_data["sub_category_1"] = (
                category_path_elements[2].text if num_categories > 2 else "Unknown"
            )
            product_data["sub_category_2"] = (
                category_path_elements[3].text if num_categories > 3 else "Unknown"
            )
            logging.info(f"------------PRODUCT DATA------------>{product_data}")
            self.all_products_data.append(product_data)
            logging.info(
                "---------------------------------------------------------------------------------------------------"
            )
            logging.info("")
            logging.info("")
        df_products_data = pd.DataFrame(self.all_products_data)
        os.makedirs(os.path.join(self.base_dir, "data", "raw"), exist_ok=True)
        output_dir = os.path.join(self.base_dir, "data", "raw")
        logging.info(output_dir)
        columns_order = [
            "sku",
            "name",
            "link",
            "brand",
            "main_category",
            "sub_category_1",
            "sub_category_2",
            "origin",
            "original_price",
            "price_with_discount",
            "discount_applicated",
            "promo",
            "warranty",
            "stars_count",
            "opinions"
        ]
        df_products_data_final = df_products_data.reindex(columns_order, axis=1)
        logging.info(f"COLUMNAS ORDENADAS: {df_products_data_final.columns}")
        df_products_data_final.to_csv(
            os.path.join(output_dir, "products_data.csv"),
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )
