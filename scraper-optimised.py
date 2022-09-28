from pathlib import Path
import re
from selenium import webdriver
from pathlib import Path
from bs4 import BeautifulSoup as soup
from supabase import create_client, Client
from decouple import config


class Scraper():
    def __init__(self) -> None:
        self.path = str(Path(__file__).parent / "chromedriver.exe")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        # attach chrome_options to driver
        self.driver = webdriver.Chrome(
            self.path, chrome_options=chrome_options)
        self.url = config('URL')
        self.key = config('API_KEY')
        self.client: Client = create_client(self.url, self.key)

    def startScraper(self):
        self.driver.get(
            "https://liquidassets.hibid.com/catalog/397846/46-x-macbook-pro--new-65--televisions--monitors-and-furniture/?ipp=100")
        pageSource = self.driver.page_source
        soup_data = soup(pageSource, 'lxml')
        baseUrl = "https://liquidassets.hibid.com"
        # soup find tag h2
        requested_data = soup_data.find_all(
            'div', {'class': 'lot-tile col-md-3 col-lg-2 p-x-xs px-md-1'})
        self.data = []
        for row in requested_data:
            flag = row.attrs.get('id', False)
            if not flag:
                continue
            title = row.contents[1].find('a').text
            url = baseUrl + row.contents[1].find('a').attrs.get('href')
            lines = re.sub(
                '\n*\n', '\n', row.contents[1].text.replace('\t', '')).split('\n')
            highest_bid = lines[13]
            bids = lines[15].split("Bid")[0]

            item = {}
            item['title'] = title
            item['url'] = url
            # item['price'] = int(float(highest_bid.replace(" ", "").split("AUD")[0].replace(",", "")))
            item['price'] = re.findall(r'\d+', highest_bid.replace(',', ""))[0]
            item['bids'] = int(bids)
            self.data.append(item)

    def writeRecords(self):
        for item in self.data:
            query = self.client.table("Products").insert(item).execute()

    def _run(self):
        self.startScraper()
        self.writeRecords()


s = Scraper()
s._run()
