from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config.logger import LoggerConfig

class ExtractElements:
    def __init__(self, __driver__):
        self.driver = __driver__
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    def safe_find_elements(self, by, path, multiple=False, timeout=20):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((by, path)))
            if multiple:
                self.logger.info("MULTIPLE")
                elements = self.driver.find_elements(by, path)
                return elements if elements else []
            else:
                self.logger.info("ELEMENT")
                element = self.driver.find_element(by, path)
                return element if element else None
        except Exception as e:
            self.logger.error("Fallo al obtener el texto:", str(e))
            return None