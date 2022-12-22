"""!@package pytrader

Algorithmic Trading Program

@author Geoff S. derber
@version HEAD
@date 2022
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

@file lib/nasdaqclient/__init__.py

    Contains global variables for the pyTrader program.

"""

# System Libraries
# import os
import requests
# import sys
from datetime import date

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.mysql import etf_info
from pytrader.libs.clients.mysql import stock_info
from pytrader.libs.utilities import text

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)
colortext = text.ConsoleText()


class NasdaqClient():
    """
    NasdaqClient

    """

    def __init__(self, *args, **kwargs):
        self.investments = kwargs['investments']
        if self.investments == "stocks":
            logger.debug("Investments: Stocks")
        elif self.investments == "etf":
            logger.debug("Investments: ETFs")
        logger.debug("Investments: %s", self.investments)

        return None

    def update_etf_database(self, table_row):
        ticker = table_row["symbol"]
        name = table_row["companyName"]

        db = etf_info.EtfInfo()
        row = db.select(ticker)
        logger.debug("Row: %s", row)

        if row is None:
            db.insert(ticker, name)
        else:
            if row["first_listed"] is None:
                db.update_last_seen(ticker, name, first_listed=date.today())
            else:
                db.update_last_seen(ticker, name)

    def update_stock_database(self, table_row):
        ticker = table_row["symbol"]
        name = table_row["name"]
        country = table_row["country"]
        industry = table_row["industry"]
        sector = table_row["sector"]

        db = stock_info.StockInfo()
        row = db.select(ticker)

        if row is None:
            db.insert(ticker, name, country, industry, sector)
        else:
            if row["first_listed"] is None:
                db.update_last_seen(ticker,
                                    name,
                                    country,
                                    industry,
                                    sector,
                                    first_listed=date.today())
            else:
                db.update_last_seen(ticker, name, country, industry, sector)

    def update_database(self, table_row):
        if self.investments == "stocks":
            self.update_stock_database(table_row)
        elif self.investments == "etf":
            logger.debug("Updating ETF info")
            self.update_etf_database(table_row)

    def check_symbol(self, data, ticker):
        return any(row["symbol"] == ticker for row in data["rows"])

    def mark_delisted(self, table):
        logger.debug("Begin Function")
        db = etf_info.EtfInfo()
        all_tickers = db.select_all_tickers()
        # logger.debug("All tickers: %s", all_tickers)

        if all_tickers:
            for item in all_tickers:
                ticker = item["ticker"]
                logger.debug("Ticker: %s", ticker)
                if not self.check_symbol(table, ticker):
                    db.update_delisted(ticker)

        return None

    def download_list(self, *args, **kwargs):
        headers = {
            "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        }

        url = "https://api.nasdaq.com/api/screener/"
        url = url + self.investments
        url = url + "?tableonly=true&limit=25&offset=0&download=true"
        investments_url = requests.get(url, headers=headers, timeout=5)

        json_data = investments_url.json()
        table = json_data["data"]

        if self.investments == "etf":
            table = table["data"]

        for table_row in table["rows"]:
            logger.debug("Table Row: %s", table_row)
            self.update_database(table_row)

        #self.mark_delisted(table)


# class Stocks(Investments):

#     def __init__(self):
#         self.investments = "stocks"
#         super(Stocks, self).__init__()
#         return None

#     def get_ticker_list(self, *args, **kwargs):
#         tickers = []
#         investments = stocks.StockInfo()
#         self.tickers = investments.get_ticker_list()

#         if len(tickers) > 0:
#             return self.tickers
#         else:
#             return self.download_list()

# class Etfs(Investments):

#     def __init__(self):
#         self.investments = "etf"
#         super(Etfs, self).__init__()
#         return None

#     def get_ticker_list(self, *args, **kwargs):
#         tickers = []
#         investments = etfs.EtfInfo()
#         self.tickers = investments.get_ticker_list()

#         if len(tickers) > 0:
#             return self.tickers
#         else:
#             return self.download_list()

#     def get_history(self, *args, **kwargs):
#         if "period" in kwargs:
#             period = kwargs["period"]
#         else:
#             period = "1d"

#         if "interval" in kwargs:
#             interval = kwargs["interval"]
#         elif period == "1d":
#             interval = "1m"
#         else:
#             interval = "1d"

#         history_data = self.stock.history(period=period,
#                                           interval=interval,
#                                           prepost=True)

#         # download_data = self.stock.download(period=period,
#         #                                    interval=interval,
#         #                                    prepost=True)

#         return history_data

#     def get_option_chain(self, *args, **kwargs):
#         expiry_dates = self.stock.options

#         for item in expiry_dates:
#             option_chain = self.stock.option_chain(item)
#             print(option_chain)
#         return None

#     def get_shares_outstanding(self, *args, **kwargs):
#         return self.stock.info["sharesOutstanding"]

#     def print_history(self, *args, **kwargs):
#         if "period" in kwargs:
#             period = kwargs["period"]
#         else:
#             period = "1d"

#         for item in self.stock.download(period=period):
#             print(item)

#         return None
