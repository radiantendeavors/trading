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
# System Libraries
import re
from typing import Optional

import numpy
# 3rd Party Libraries
import pandas
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ReadTimeout

# Other Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.contract_universe import \
    IbkrContractUniverse
# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## Instance of Logging class
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrWebScraper():
    """!
    Scrapes Interactive Brokers Website for data.
    """
    ## Base URL
    base_url = "https://www.interactivebrokers.com/en/"
    exchange_listings = pandas.DataFrame()
    anchors = []
    exchange_assets = {}
    exchange_assets_pages = {}
    exchange_asset_page_assets = {}
    session = requests.Session()
    user_agent = "Mozilla/5.0 6(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    user_agent += " Chrome/117.0.0.0 Safari/537.36"
    session.headers.update({"User-Agent": user_agent})

    ibkr_asset_class_sort_order = {
        "ETF": 1,
        "STK": 2,
        "BOND": 3,
        "BILL": 4,
        "IND": 5,
        "FUTGRP": 6,
        "OPTGRP": 7,
        "WAR": 8
    }

    def filter_assets(self, currencies: list) -> None:
        """!
        Filters assets to eliminate bad values

        @param currencies:

        @return None
        """
        # Rename first row to column header
        self.exchange_listings = self.exchange_listings.rename(
            columns=self.exchange_listings.iloc[0])

        # Drop rows where atleast one element is missing
        self.exchange_listings = self.exchange_listings.dropna()

        # if there is row with text 'symbol', exclude that
        self.exchange_listings = self.exchange_listings[self.exchange_listings.Symbol != 'Symbol']

        # Drop exact matches for duplicate Product Descriptions
        self.exchange_listings = self.exchange_listings.drop_duplicates("Product Description")

        self.exchange_listings = self.exchange_listings[self.exchange_listings.Currency.isin(
            currencies)]

        self._find_unique_rows()

        self.exchange_listings = self.exchange_listings.sort_values(
            by=["IB Symbol", "Asset Class Sort"], ascending=[True, True])
        self.exchange_listings = self.exchange_listings.reset_index(drop=True)
        logger.debug("Dataframe:\n%s", self.exchange_listings)

    def get_exchange_listings(self, regions: list) -> None:
        """!
        Provides a list of exchanges to get assets from.

        @return None
        """
        exchange_listing_url = self.base_url + "index.php?f=1562"

        for region in regions:
            url = exchange_listing_url + "&p=" + region
            response = self.session.get(url, timeout=10)

            soup = BeautifulSoup(response.content, 'lxml')

            # This escape is necessary.
            text = soup.find_all('a', href=re.compile('index.php\?f=2222'))

            for anchor in text:
                self.anchors.append(anchor['href'])

            soup.decompose()

    def get_asset_classes(self) -> None:
        """!
        Gets a list of asset classes each exchange supports.

        @return None
        """
        for item in self.anchors:
            exchange_url = self.base_url + item

            response = self.session.get(exchange_url, timeout=10)

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

            soup.decompose()

        logger.debug9("Exchange Assets: %s", self.exchange_assets)

    def get_asset_class_pages(self, allowed_asset_classes: Optional[list] = None) -> None:
        """!
        Get's the number of pages for each asset class for each exchange.

        @return None
        """
        logger.debug9("Exchange Assets: %s", self.exchange_assets)

        for exchange, asset_classes in self.exchange_assets.items():
            for asset_class in asset_classes:
                if allowed_asset_classes is None or asset_class in allowed_asset_classes:
                    self._get_pages(exchange, asset_class)

        for key, value in self.exchange_assets_pages.items():
            logger.debug9("URL: %s, Pages: %s", key, value)

    def get_assets(self) -> None:
        """!
        Get all assets from interactive brokers website.

        @param currencies: allowed currencies"""
        header_url = list(self.exchange_assets_pages)[0]
        self._get_table_header(header_url)

        if self.exchange_listings.iloc[0, 0] == 'IB Symbol':
            self.exchange_listings.iloc[0, 1] = 'Product Description'

            for asset_url, pages in self.exchange_assets_pages.items():
                self._create_table_data(asset_url, pages)
        else:
            logger.critical("Interactive Brokers Changed their website!")
            logger.critical("No data was downloaded.")

    def to_sql(self) -> None:
        """!
        Saves the data to an sql database.

        @return None
        """
        database = IbkrContractUniverse()
        numrows = len(self.exchange_listings.index)

        # We iterate the rows rather than using pandas to_sql so we can ensure we don't add
        # duplicates each time this is run.
        for index, row in self.exchange_listings.iterrows():
            logger.debug("Inserting row %s of %s", index, numrows)
            logger.debug("Row: %s", row)
            columns = [
                row["Long ID"], row["IB Symbol"], row["Product Description"], row["Symbol"],
                row["Currency"], row["Asset Class"], row["Exchange"]
            ]

            database.insert(columns)

    def to_csv(self) -> None:
        """!
        Saves the data to a CSV file.

        @return None
        """
        self.exchange_listings.to_csv('scraped_data.csv', index=False)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _create_table_data(self, asset_url: str, pages: int) -> None:
        asset_class = self.exchange_asset_page_assets[asset_url]
        exchange = self._get_exchange(asset_url, asset_class)

        if pages == 0:
            self._get_table_data(asset_url, asset_class, exchange)
        else:
            page = 1
            while page <= pages:
                page_url = asset_url + "&limit=100&page=" + str(page)
                self._get_table_data(page_url, asset_class, exchange)
                page += 1

        logger.debug("Exchange Listings:\n%s", self.exchange_listings)

    def _find_unique_rows(self) -> None:
        # ==========================================================================================
        #
        # FIXME: Ensuring we don't have any duplicates is hard.  This is a half-assed solution.  It
        # is still an improvement over what I had.
        #
        # Sometimes ETFs will appear as Stocks with the product description ALL CAPS, but with other
        # minor changes.  For example
        #
        # Symbol | Product Description               | Asset Class
        # -------+-----------------------------------+------------
        # VT     | VANGUARD TOT WORLD STK ETF        | STK
        # VT     | Vanguard Total World Stock ETF    | ETF
        # VT     | CBOE S&P 500 Three Month Variance | IND  (To make it even more complicated)
        #
        # And that is within the USD Currency.
        #
        # ==========================================================================================
        self.exchange_listings["Long ID"] = self.exchange_listings[
            "IB Symbol"] + "." + self.exchange_listings["Asset Class"]
        self.exchange_listings = self.exchange_listings.drop_duplicates("Long ID")

    def _get_exchange(self, asset_url: str, asset_class: str) -> str:
        if asset_class == "IND":
            exchange_half = asset_url.split("=")[2]
            exchange = exchange_half.split("&")[0]
            logger.debug("Asset URL: %s", asset_url)
            logger.debug("Exchange: %s", exchange)

            # Ensure exchanges are upper case
            return exchange.upper()

        return "SMART"

    def _get_table_data(self, asset_url: str, asset_class: str, exchange: str) -> None:
        """
        Retrieves data from asset_url

        @param asset_url:
        @param asset_class:
        @param exchange:

        Returns None
        """
        try:
            response = self.session.get(asset_url, timeout=30)
            logger.debug('\nDownloading URL: %s', response.url)
            if response.status_code != 200:
                logger.warning('The Status Code from Requests: %s', response.status_code)
            else:
                logger.debug9('The Status Code from Requests: %s', response.status_code)

            soup = BeautifulSoup(response.content, 'lxml')

            table = soup.find_all('table')[2]
            page_dataframe = pandas.DataFrame(columns=range(0, 4), index=[0])

            for row_marker, row in enumerate(table.find_all('tr')):
                columns = row.find_all(['td'])

                try:
                    page_dataframe.loc[row_marker] = [column.get_text() for column in columns]
                except ValueError:
                    # Ensure we don't fail out if column.get_text() returns an empty list.
                    continue

            page_dataframe["Asset Class"] = asset_class
            page_dataframe["Exchange"] = exchange

            # If the description says it's an ETF, ensure we capture it as an ETF.
            # We really need to check "ETF", "Etf", maybe "EtF", and "etf"
            # I'd be easier to check upper case, but that doesn't work with a dataframe.
            page_dataframe["Asset Class"] = numpy.where(
                page_dataframe[1].str.contains("etf", case=False, regex=False), "ETF",
                page_dataframe["Asset Class"])
            page_dataframe["Asset Class"] = numpy.where(
                page_dataframe[1].str.contains("etn", case=False, regex=False), "ETN",
                page_dataframe["Asset Class"])

            page_dataframe["Asset Class Sort"] = self.ibkr_asset_class_sort_order[asset_class]

            self.exchange_listings = pandas.concat([self.exchange_listings, page_dataframe],
                                                   ignore_index=True)

            soup.decompose()

        except ReadTimeout as msg:
            logger.critical("Timout Reached for %s", asset_url)
            logger.debug("Error Message: %s", msg)

    def _get_table_header(self, asset_url: str) -> None:
        """
        Retrieves the header rows from asset_url

        @param asset_url:

        Returns None
        """
        try:
            response = self.session.get(asset_url, timeout=30)
            logger.debug('\nDownloading URL: %s', response.url)
            if response.status_code != 200:
                logger.warning('The Status Code from Requests: %s', response.status_code)
            else:
                logger.debug9('The Status Code from Requests: %s', response.status_code)

            soup = BeautifulSoup(response.content, 'lxml')

            table = soup.find_all('table')[2]
            page_dataframe = pandas.DataFrame(columns=range(0, 4), index=[0])

            for row_marker, row in enumerate(table.find_all('tr')):
                columns = row.find_all(['th'])

                if len(columns) > 0:
                    try:
                        page_dataframe.loc[row_marker] = [column.get_text() for column in columns]
                    except ValueError as message:
                        logger.error("Failed to get header row: %s", message)

            page_dataframe["Asset Class"] = "Asset Class"
            page_dataframe["Exchange"] = "Exchange"
            page_dataframe["Asset Class Sort"] = "Asset Class Sort"

            self.exchange_listings = pandas.concat([self.exchange_listings, page_dataframe],
                                                   ignore_index=True)

            soup.decompose()

        except ReadTimeout as msg:
            logger.critical("Timout Reached for %s", asset_url)
            logger.debug("Error Message: %s", msg)

    def _get_pages(self, exchange, asset_class):
        exchange_url = exchange + asset_class

        response = self.session.get(exchange_url, timeout=10)

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
