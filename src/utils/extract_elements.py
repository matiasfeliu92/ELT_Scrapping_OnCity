from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ExtractElements:
    def __init__(self, __driver__):
        self.driver = __driver__

    def safe_find_elements(self, by, path, multiple=False, timeout=20):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.visibility_of_element_located((by, path)))
            if multiple:
                print("MULTIPLE")
                elements = self.driver.find_elements(by, path)
                return elements if elements else []
            else:
                print("ELEMENT")
                element = self.driver.find_element(by, path)
                return element if element else None
        except Exception as e:
            print("Fallo al obtener el texto:", e)
            return None