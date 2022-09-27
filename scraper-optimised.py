from pathlib import Path
import re
from selenium import webdriver
from pathlib import Path
from bs4 import BeautifulSoup as soup

path = Path(__file__).parent / "chromedriver"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
# attach chrome_options to driver
driver = webdriver.Chrome(path, chrome_options=chrome_options)

driver.get(
    "https://liquidassets.hibid.com/catalog/397846/46-x-macbook-pro--new-65--televisions--monitors-and-furniture/?ipp=100")
pageSource = driver.page_source
soup_data = soup(pageSource, 'lxml')
baseUrl = "https://liquidassets.hibid.com"
# soup find tag h2
requested_data = soup_data.find_all(
    'div', {'class': 'lot-tile col-md-3 col-lg-2 p-x-xs px-md-1'})
data = {}
for row in requested_data:
    text = row.contents[1].text
    Title = row.contents[1].find('a').text
    url = baseUrl + row.contents[1].find('a').attrs.get('href')
    lines = re.sub(
        '\n*\n', '\n', requested_data[0].contents[1].text.replace('\t', '')).split('\n')
    highest_bid = lines[13]
    data[url] = [Title, highest_bid]
