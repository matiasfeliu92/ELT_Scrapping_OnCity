from scripts.Scrapper import Scrap

if __name__ == "__main__":
    scrap = Scrap()
    scrap.extract_links()
    scrap.extract_data()