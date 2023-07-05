"""!
@package pytrader.libs.clients.broker.ibkr.webscraper

Creates a basic interface for interacting with a broker

@author G. S. Derber
@date 2022-2023
@copyright GNU Affero General Public License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

@file pytrader/libs/clients/broker/ibkr/webscraper/__init__.py

Creates a basic interface for interacting with a broker
"""
# Standard Libraries
import re
import requests

# 3rd Party Libraries
import pandas

from bs4 import BeautifulSoup

# Standard Library Overrides
from pytrader.libs.system import logging

# Other Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## Instance of Logging class
logger = logging.getLogger(__name__)

## Headers
requests_headers = {
    'User-Agent':
    'Mozilla/5.0 6(Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
}

## Base URL
base_url = "https://www.interactivebrokers.com/en/"

## Exchange Listing URL
url = base_url + "index.php?f=exchanges"

##
IBKR_ASSET_CLASS_LIST = [
    "STK", "FUT", "OPT", "IND", "FOP", "CASH", "BAG", "WAR", "BOND", "CMDTY", "NEWS", "FUND"
]

IBKR_ASSET_CLASS_SORT = {
    "STK": 1,
    "ETF": 2,
    "BOND": 3,
    "BILL": 4,
    "IND": 5,
    "FUTGRP": 6,
    "OPTGRP": 7,
    "WAR": 8
}


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrWebScraper():

    def __init__(self):
        self.anchors = []
        self.exchange_assets = {}
        self.exchange_assets_pages = {}
        self.exchange_asset_page_assets = {}

    def get_exchange_listings(self):
        response = requests.get(url, headers=requests_headers, timeout=10)

        soup = BeautifulSoup(response.content, 'lxml')
        text = soup.find_all('a', href=re.compile('index.php\?f=2222'))

        for anchor in text:
            self.anchors.append(anchor['href'])

    def get_asset_classes(self):
        for item in self.anchors:
            exchange_url = base_url + item

            response = requests.get(exchange_url, headers=requests_headers, timeout=10)

            soup = BeautifulSoup(response.content, 'lxml')
            text = soup.find_all('a', id=re.compile('[A-Z][A-Z][A-Z]'))

            if text:
                id_list = []
                for item in text:
                    id_list.append(item.get('id'))
                    logger.debug9("Item: %s", item)
                    logger.debug9("ID: %s", item.get('id'))

                self.exchange_assets[exchange_url] = id_list
            else:
                logger.debug9("Text: %s", text)

        logger.debug9("Exchange Assets: %s", self.exchange_assets)

    def get_asset_class_pages(self):
        logger.debug9("Exchange Assets: %s", self.exchange_assets)

        for exchange, asset_classes in self.exchange_assets.items():
            for asset_class in asset_classes:
                exchange_url = exchange + asset_class

                response = requests.get(exchange_url, headers=requests_headers, timeout=10)

                soup = BeautifulSoup(response.content, 'lxml')
                text = soup.find_all('a', href=re.compile('page='))

                pages = []

                if text:
                    for anchor in text:
                        anchor_text = anchor['href']
                        pages.append(int(anchor_text.split("=")[8]))
                        logger.debug9("URL: %s, Pages: %s", exchange_url, pages)

                    page = max(pages)
                    logger.debug8("URL: %s, Pages: %s", exchange_url, page)
                    self.exchange_assets_pages[exchange_url] = page
                    self.exchange_asset_page_assets[exchange_url] = asset_class
                else:
                    self.exchange_assets_pages[exchange_url] = 0
                    self.exchange_asset_page_assets[exchange_url] = asset_class

        for key, value in self.exchange_assets_pages.items():
            logger.debug9("URL: %s, Pages: %s", key, value)

    def get_table_data(self, asset_url, asset_class, data):
        """
        The function to retreive data and header using requests module from url1 and url2
            If data=True, retreive only Data from the table in the url
            If data=False, retreive the header from the table in the url

        Returns df
        """
        response = requests.get(asset_url, headers=requests_headers, timeout=30)
        logger.debug('\nDownloading URL: %s', response.url)
        if response.status_code != 200:
            logger.warning('The Status Code from Requests: %s', response.status_code)
        else:
            logger.debug9('The Status Code from Requests: %s', response.status_code)
        soup = BeautifulSoup(response.content, 'lxml')

        table = soup.find_all('table')[2]
        df = pandas.DataFrame(columns=range(0, 4), index=[0])

        for row_marker, row in enumerate(table.find_all('tr')):

            if data is True:
                columns = row.find_all(['td'])  # Capture only the Table Data Cells.
            else:
                columns = row.find_all(['th'])  # Capture only the Table Header Cells.
            try:
                df.loc[row_marker] = [column.get_text() for column in columns]
            except ValueError:
                # It's a safe way to handle when [column.get_text() for column in columns] is empty list.
                continue

        df["Asset Class"] = asset_class
        if data is True:
            df["Asset Class Sort"] = IBKR_ASSET_CLASS_SORT[asset_class]
        else:
            df["Asset Class Sort"] = "Asset Class Sort"

        return df

    def get_assets(self, currency: str = "USD"):
        header_url = list(self.exchange_assets_pages.keys())[0]
        df = self.get_table_data(header_url, "Asset Class", data=False)

        if df.iloc[0, 0] == 'IB Symbol':
            df.iloc[0, 1] = 'Product Description'
        else:
            logger.warning(
                "WARNING !!!.Some Change in the Header Data of IB webitse. ***CHECK ALL DATA***")

        for asset_url, pages in self.exchange_assets_pages.items():
            asset_class = self.exchange_asset_page_assets[asset_url]
            if pages == 0:
                df_table_data = self.get_table_data(asset_url, asset_class, data=True)
                df = pandas.concat([df, df_table_data])
            else:
                page = 1
                while page <= pages:
                    page_url = asset_url + "&limit=100&page=" + str(page)
                    df_table_data = self.get_table_data(page_url, asset_class, data=True)
                    df = pandas.concat([df, df_table_data])
                    page += 1

        df = df.rename(columns=df.iloc[0])  # Rename first row to column header
        df = df.dropna()  # Drop rows where atleast one element is missing
        df = df[df.Symbol != 'Symbol']  # if there is row with text 'symbol', exclude that
        df = df[df.Currency == currency]
        df = df.sort_values(by=["IB Symbol", "Asset Class Sort"], ascending=[True, False])
        df = df.drop_duplicates("IB Symbol")
        #df = df[df.Symbol != 'NIFTY'] # If there is row with 'NIFTY50', exclude that
        #df = df[df.Symbol != 'BANKNIFTY'] # If there is row with 'BANKNIFTY', exclude that
        #df = df[df.Symbol != 'USDINR'] # If there is row with 'USDINR', exclude that
        #df = df[df.Symbol != 'EURINR'] # If there is row with 'EURINR', exclude that
        #df = df[df.Symbol != 'GBPINR'] # If there is row with 'GBPINR', exclude that
        #df = df[df.Symbol != 'JPYINR'] # If there is row with 'JPYINR', exclude that
        df = df.reset_index(drop=True)
        logger.debug("Dataframe:\n%s", df)
        df.to_csv('scraped_data.csv', index=False)  # dont write row names
