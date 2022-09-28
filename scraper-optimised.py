from selenium import webdriver
from pathlib import Path
from bs4 import BeautifulSoup as soup
from supabase import create_client, Client
from decouple import config
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import re
import sys
import logging

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
        self.supa_client: Client = create_client(self.url, self.key)

        # self.sendgrid_api_key = config('SENDGRID_API_KEY')

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

            item['price'] = re.findall(r'\d+', highest_bid.replace(',', ""))[0]
            item['bids'] = int(bids)
            self.data.append(item)

    def writeRecords(self):
        for item in self.data:
            query = self.supa_client.table("Products").insert(item).execute()

    def getData(self):
        try:
            for item in self.data:
                message_queue = []
                query : Client = self.supa_client.table("Products").select("*").filter("url", "ilike", f"{item['url']}").order("created_at", desc=True).execute()
                previous = query.data[0]
                if item['price'] > previous['price']:
                    message = f'Price of {item["title"]} increased from {previous["price"]} to {item["price"]} \n Click here to view {item["url"]} \n'
                    message_queue.append(message)
                
        except Exception as e:
            with open('logfile.txt', 'a+') as file:
                file.write("hello")
                file.write('\n')

        return message_queue

    def sendMessage(self):
        emailTemplate = ''
        messages = self.getData()
        if len(messages) == 0:
            from datetime import datetime
            now = datetime.now()
            sys.exit(f"No updates found at {now}")
    
        for message in messages:
            emailTemplate += message

        try:
            fromEmail = config('FROM_EMAIL')
            fromPassword = config('FROM_PASSWORD')
            toEmail = config('TO_EMAIL')

            message = MIMEMultipart()
            message['From'] = fromEmail
            message['To'] = toEmail
            message['Subject'] = 'Auction Price Updates' 

            message.attach(MIMEText(emailTemplate, 'plain'))

            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(fromEmail, fromPassword)
            text = message.as_string()
            session.sendmail(fromEmail, toEmail, text)
            session.quit()

        except Exception as e:
            print('Something went wrong...', e)

    def _run(self):
        self.startScraper()
        self.sendMessage()
        # self.writeRecords()


s = Scraper()
s._run()
