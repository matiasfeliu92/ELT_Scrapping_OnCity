import random
import time
from selenium.webdriver.common.by import By

from src.config.logger import LoggerConfig
from src.config.scraping_settings import ScrapingSettings
from src.utils.extract_elements import ExtractElements


class Scraping:
    def __init__(self, __link__):
        self.link = __link__
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.scraping_settings = ScrapingSettings()
        self.driver = self.scraping_settings.get_chrome_driver()
        self.extract_elements = ExtractElements(self.driver)
        self.product_data = {}

    def run(self):
        if "megatone.net" in self.link:
            self.logger.info("Iniciando scraping para Megatone")
            self.logger.info(f"Accediendo al enlace: {self.link}")
            self.driver.get(self.link)
            time.sleep(random.uniform(2, 5))
            list_price = None
            cash_price = None
            stock = None
            installments_dict = None
            product_title = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["PRODUCT_TITLE"])
            product_sku = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["SKU"])
            brand = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["BRAND"])
            category_path_nav = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["CATEGORY_PATH"])
            price_mostrado = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.MEGATONE_SELECTORS["PRICE_MOSTRADO"])
            price_tachado = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["PRICE_TACHADO"])
            price_1_pago = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["PRICE_1_PAGO"])
            installments = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.MEGATONE_SELECTORS["INSTALLMENTS"], multiple=True)
            sin_stock = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["SIN_STOCK"])
            con_stock = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["CON_STOCK"])
            description = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MEGATONE_SELECTORS["DESCRIPTION"], multiple=True)

            category_path_links = category_path_nav.find_elements(By.TAG_NAME, "a")
            category_path_links_text = [link.text for link in category_path_links]
            self.logger.info(f"Category Path: {category_path_links_text}")

            self.logger.info("PRICES DATA")
            if price_tachado and price_mostrado:
                list_price = price_tachado
                cash_price = price_mostrado
            elif price_mostrado and price_1_pago:
                list_price = price_mostrado
                cash_price = price_1_pago
            elif sin_stock and not con_stock and not price_1_pago and not price_mostrado and not price_tachado:
                list_price = None
                cash_price = None


            print("List Price:", list_price.text if list_price else "") 
            print("Cash Price:", cash_price.text if cash_price else "")
            
            self.logger.info("INSTALLMENTS DATA")
            installments_list = []
            if installments:
                for installment in installments:
                    installment_text = installment.find_elements(By.TAG_NAME, "span")
                    self.logger.info("-----")
                    self.logger.info("-----")
                    self.logger.info("-----")
                    for inst in installment_text:
                        if "Sin Interés" not in inst.text and "$" not in inst.text:
                            self.logger.info(f" - {inst.text}")
                            installments_list.append(inst.text)
            else:
                installments_dict = None
            installments_dict = {f"Opcion {i+1}": cuota for i, cuota in enumerate(installments_list)}
            self.logger.info(f"Installments: {installments_dict}")

            if con_stock and not sin_stock:
                stock = True
            elif sin_stock and not con_stock:
                stock = False
            self.logger.info(f"Descriptions: {description}")

            self.product_data["name"] = product_title.text if product_title else ""
            self.product_data["sku"] = product_sku.text if product_sku else ""
            self.product_data["brand"] = brand.text if brand else ""
            self.product_data["main_category"] = category_path_links_text[1] if len(category_path_links_text)>1 else ""
            self.product_data["sub_category"] = category_path_links_text[2] if len(category_path_links_text)>2 else ""
            self.product_data["list_price"] = list_price.text if list_price else ""
            self.product_data["cash_price"] = cash_price.text if cash_price else ""
            self.product_data["installments"] = installments_dict
            self.product_data["stock"] = stock
            self.product_data["store"] = "Megatone"
            self.product_data["link"] = self.link
            self.logger.info(f"------------PRODUCT DATA------------>{self.product_data}")
            self.logger.info(
                "---------------------------------------------------------------------------------------------------"
            )
            self.logger.info("")
            self.logger.info("")
            return self.product_data
        
        elif "fravega.com" in self.link:
            self.logger.info("Iniciando scraping para Fravega")
            self.logger.info(f"Accediendo al enlace: {self.link}")
            self.driver.get(self.link)
            time.sleep(random.uniform(2, 5))
            list_price = None
            cash_price = None
            producto_no_disponible = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.FRAVEGA_SELECTORS["PRODUCTO_NO_DISPONIBLE"])
            if producto_no_disponible:
                self.product_data["name"] = ""
                self.product_data["sku"] = ""
                self.product_data["brand"] = ""
                self.product_data["main_category"] = ""
                self.product_data["sub_category"] = ""
                self.product_data["list_price"] = ""
                self.product_data["cash_price"] = ""
                self.product_data["installments"] = ""
                self.product_data["stock"] = False
                self.product_data["store"] = "Fravega"
                self.product_data["link"] = self.link
                self.logger.info(f"------------PRODUCT DATA------------>{self.product_data}")
                self.logger.info(
                    "---------------------------------------------------------------------------------------------------"
                )
                self.logger.info("")
                self.logger.info("")
                return self.product_data
            product_title = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.FRAVEGA_SELECTORS["PRODUCT_TITLE"])
            product_sku = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.FRAVEGA_SELECTORS["SKU"])
            brand = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.FRAVEGA_SELECTORS["BRAND"])
            category_path_nav = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.FRAVEGA_SELECTORS["CATEGORY_PATH"], multiple=True)
            price_mostrado = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.FRAVEGA_SELECTORS["PRICE_MOSTRADO"])
            price_tachado = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.FRAVEGA_SELECTORS["PRICE_TACHADO"])
            installments = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.FRAVEGA_SELECTORS["INSTALLMENTS"], multiple=True)

            category_path_links_text = [link.text for link in category_path_nav if link.get_attribute("itemprop") == "name" and link.text != "" and link.text != "Frávega"]
            self.logger.info(f"Category Path: {category_path_links_text}")

            if price_tachado and price_mostrado:
                list_price = price_tachado
                cash_price = price_mostrado
            elif price_mostrado and not price_tachado:
                list_price = price_mostrado
                cash_price = None

            print("List Price:", list_price.text if list_price else "") 
            print("Cash Price:", cash_price.text if cash_price else "")

            self.logger.info("INSTALLMENTS DATA")
            installments_list = [instalment.text for instalment in installments if instalment.text.isdigit()]
            self.logger.info(installments_list)
            installments_dict = {f"Opcion {i+1}": cuota for i, cuota in enumerate(installments_list)}

            self.product_data["name"] = product_title.text if product_title else ""
            self.product_data["sku"] = product_sku.text.replace("Artículo: ", "") if product_sku else ""
            self.product_data["brand"] = brand.get_attribute("href").replace("https://www.fravega.com/l/?marcas=", "") if brand else ""
            self.product_data["main_category"] = category_path_links_text[-2] if len(category_path_links_text)>1 else ""
            self.product_data["sub_category"] = category_path_links_text[-1] if len(category_path_links_text)>1 else ""
            self.product_data["list_price"] = list_price.text if list_price else ""
            self.product_data["cash_price"] = cash_price.text if cash_price else ""
            self.product_data["installments"] = installments_dict
            self.product_data["stock"] = True
            self.product_data["store"] = "Fravega"
            self.product_data["link"] = self.link
            self.logger.info(f"------------PRODUCT DATA------------>{self.product_data}")
            self.logger.info(
                "---------------------------------------------------------------------------------------------------"
            )
            self.logger.info("")
            self.logger.info("")
            return self.product_data

        elif "musimundo.com" in self.link:
            self.logger.info("Iniciando scraping para Musimundo")
            self.logger.info(f"Accediendo al enlace: {self.link}")
            self.driver.get(self.link)
            time.sleep(random.uniform(2, 5))
            list_price = None
            cash_price = None
            stock = None
            product_title = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MUSIMUNDO_SELECTORS["PRODUCT_TITLE"])
            product_sku = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MUSIMUNDO_SELECTORS["SKU"])
            brand = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.MUSIMUNDO_SELECTORS["BRAND"])
            category_path_nav = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.MUSIMUNDO_SELECTORS["CATEGORY_PATH"], multiple=True)
            price_mostrado = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.MUSIMUNDO_SELECTORS["PRICE_MOSTRADO"])
            price_tachado = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.MUSIMUNDO_SELECTORS["PRICE_TACHADO"])
            installments = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.MUSIMUNDO_SELECTORS["INSTALLMENTS"], multiple=True)
            button_ad_to_cart = self.extract_elements.safe_find_elements(By.ID, self.scraping_settings.MUSIMUNDO_SELECTORS["BUTTON_ADD_TO_CART"])

            category_path_links_text = [link.find_element(By.TAG_NAME, "a").text for link in category_path_nav if link.get_attribute("data-test-breadcrumbs") == "breadcrumb"]
            self.logger.info(f"Category Path: {category_path_links_text}")

            if price_tachado and price_mostrado:
                list_price = price_tachado
                cash_price = price_mostrado
            elif price_mostrado and not price_tachado:
                list_price = price_mostrado
                cash_price = None

            self.logger.info(f'LIST PRICE ------------------- {list_price.text}')
            self.logger.info(f'CASH PRICE ------------------- {cash_price.text}')

            self.logger.info("INSTALLMENTS DATA")
            installment_text = [installment.text for installment in installments if "cuotas" in installment.text]
            installments_dict = {f"Opcion {i+1}": cuota for i, cuota in enumerate(installment_text)}
            self.logger.info(f"Installments: {installments_dict}")

            if button_ad_to_cart:
                stock = True
            else:
                stock = False

            self.product_data["name"] = product_title.text if product_title else ""
            self.product_data["sku"] = product_sku.text if product_sku else ""
            self.product_data["brand"] = brand.text if brand else ""
            self.product_data["main_category"] = category_path_links_text[0] if len(category_path_links_text)>1 else ""
            self.product_data["sub_category"] = category_path_links_text[1] if len(category_path_links_text)>2 else ""
            self.product_data["list_price"] = list_price.text if list_price else ""
            self.product_data["cash_price"] = cash_price.text if cash_price else ""
            self.product_data["installments"] = installments_dict
            self.product_data["stock"] = stock
            self.product_data["store"] = "Musimundo"
            self.product_data["link"] = self.link
            self.logger.info(f"------------PRODUCT DATA------------>{self.product_data}")
            self.logger.info(
                "---------------------------------------------------------------------------------------------------"
            )
            self.logger.info("")
            self.logger.info("")
            return self.product_data
        elif "naldo.com.ar" in self.link:
            self.logger.info("Iniciando scraping para Naldo")
            self.logger.info(f"Accediendo al enlace: {self.link}")
            self.driver.get(self.link)
            time.sleep(random.uniform(2, 5))
            list_price = None
            cash_price = None
            stock = None
            product_title = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.NALDO_SELECTORS["PRODUCT_TITLE"])
            product_sku = self.extract_elements.safe_find_elements(By.CSS_SELECTOR, self.scraping_settings.NALDO_SELECTORS["SKU"])
            brand = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.NALDO_SELECTORS["BRAND"])
            category_path_nav = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.NALDO_SELECTORS["CATEGORY_PATH"], multiple=True)
            price_tachado = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.NALDO_SELECTORS["PRICE_TACHADO"])
            price_mostrado = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.NALDO_SELECTORS["PRICE_MOSTRADO"])
            installments = self.extract_elements.safe_find_elements(By.XPATH, self.scraping_settings.NALDO_SELECTORS["INSTALLMENTS"], multiple=True)

            category_path_links_text = [link.text for link in category_path_nav]

            if price_tachado and price_mostrado:
                price_tachado = price_tachado.text.replace(" ", "").replace("\n", "")
                price_mostrado = price_mostrado.text.replace(" ", "").replace("\n", "")
                list_price = price_tachado
                cash_price = price_mostrado
            elif price_mostrado and not price_tachado:
                price_mostrado = price_mostrado.text.replace(" ", "").replace("\n", "")
                list_price = price_mostrado
                cash_price = None

            self.logger.info(f'LIST PRICE: {list_price}')
            self.logger.info(f'CASH PRICE: {cash_price}')

            self.logger.info("INSTALLMENTS DATA")
            installment_text = [installment.text for installment in installments if "cuotas" in installment.text]
            self.logger.info(installment_text)
            installments_dict = {f"Opcion {i+1}": cuota for i, cuota in enumerate(installment_text)}
            self.logger.info(f"Installments: {installments_dict}")

            self.product_data["name"] = product_title.text if product_title else ""
            self.product_data["sku"] = product_sku.text if product_sku else ""
            self.product_data["brand"] = brand.text if brand else ""
            self.product_data["main_category"] = category_path_links_text[1] if len(category_path_links_text)>1 else ""
            self.product_data["sub_category"] = category_path_links_text[2] if len(category_path_links_text)>2 else ""
            self.product_data["list_price"] = list_price if list_price else ""
            self.product_data["cash_price"] = cash_price if cash_price else ""
            self.product_data["installments"] = installments_dict
            self.product_data["stock"] = True
            self.product_data["store"] = "Naldo"
            self.product_data["link"] = self.link
            self.logger.info(f"------------PRODUCT DATA------------>{self.product_data}")
            self.logger.info(
                "---------------------------------------------------------------------------------------------------"
            )
            self.logger.info("")
            self.logger.info("")
            return self.product_data
        else:
            return {}