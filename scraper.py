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
    'h2', {'class': 'lot-tile-lead-container-header m-t-xs m-b-xs'})
data = {}
for row in requested_data:
    url = baseUrl + row.contents[1].attrs.get('href')
    driver.get(url)
    pageSource = driver.page_source
    soup_data = soup(pageSource, 'lxml')
    Title = soup_data.find('h1').text
    required_data = soup_data.find_all("div", {"class": "col-xs-12 col-sm-6"})
    Table_info = required_data[1].contents[3].find_all('tr')
    line = required_data[1].contents[3].find_all(
        'tr')[2].text.replace('\t', '')
    line = re.sub(r'\n*\n', '\n', line)
    highest_bid = line.split('\n')[2]
    data[url] = [Title, highest_bid]
print(data)
