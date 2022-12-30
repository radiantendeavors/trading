"""!
@package pytrader.libs.security

Provides the broker client

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


@file security.py
"""
# System libraries
import random
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients import nasdaq
from pytrader.libs.clients import yahoo
from pytrader.libs.indexes import index
from pytrader.libs.securities import etf
from pytrader.libs.securities import stock

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)
min_sleeptime = 61
max_sleeptime = 121


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Securities():

    def __init__(self, *args, **kwargs):
        self.securities_list = {}
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]
            logger.debug("BrokerClient: %s", self.brokerclient)

    def __update_info_broker(self):
        logger.debug10("Begin Function")

        for item in self.securities_list:
            logger.debug2("Item: %s", item)
            logger.debug3("Investment Type: %s", self.investment_type)
            if self.investment_type == "etfs":
                security = etf.Etf(ticker_symbol=item["ticker"],
                                   brokerclient=self.brokerclient)
            elif self.investment_type == "indexes":
                security = index.Index(ticker_symbol=item["ticker"],
                                       brokerclient=self.brokerclient)
            elif self.investment_type == "stocks":
                security = stock.Stock(ticker_symbol=item["ticker"],
                                       brokerclient=self.brokerclient)

            else:
                logger.error("No investment type was selected.")

            logger.debug("Security: %s", security)
            security.update_info()

        logger.debug10("End Function")
        return None

    def __update_info_nasdaq(self):
        logger.debug10("Begin Function")
        client = nasdaq.NasdaqClient(investments=self.investment_type)
        client.download_list()
        logger.debug10("End Function")
        return None

    def __update_info_yahoo(self):
        logger.debug10("Begin Function")
        for ticker in self.securities_list:
            logger.debug("Ticker: %s", ticker["yahoo_symbol"])
            if ticker["yahoo_symbol"]:
                yahoo_symbol = ticker["yahoo_symbol"]
            else:
                yahoo_symbol = ticker["ticker"]

            yc = yahoo.YahooClient()
            yc.get_info(self.investment_type, yahoo_symbol)
            time.sleep(random.randint(min_sleeptime, max_sleeptime))

        logger.debug10("End Function")
        return None

    def __update_history_yahoo(self, bar_size, period):
        logger.debug10("Begin Function")
        for ticker in self.securities_list:
            logger.debug("Ticker: %s", ticker["yahoo_symbol"])
            if ticker["yahoo_symbol"]:
                yc = yahoo.YahooClient()
                yc.get_bar_history(self.investment_type,
                                   ticker["ticker"],
                                   ticker["yahoo_symbol"],
                                   interval=bar_size,
                                   period=period)
            time.sleep(random.randint(min_sleeptime, max_sleeptime))

        logger.debug10("End Function")
        return None

    def update_history(self, source, bar_size, period):
        logger.debug10("Begin Function")
        if self.securities_list:
            logger.debug("Index List: %s", self.index_list)
        else:
            self.get_list()

        if source == "yahoo":
            self.__update_history_yahoo(bar_size, period)
        else:
            self.__update_history_yahoo(bar_size, period)

        logger.debug("End Function")
        return None

    def update_info(self, source=None):
        logger.debug10("Begin Function")
        logger.debug("Source: %s", source)
        if self.securities_list:
            logger.debug("Index List: %s", self.securities_list)
        else:
            self.get_list()

        if source == "broker":
            self.__update_info_broker()
        elif source == "nasdaq":
            self.__update_info_nasdaq()
        elif source == "yahoo":
            self.__update_info_yahoo()
        else:
            self.__update_info_nasdaq()
            self.__update_info_yahoo()

        logger.debug("End Function")
        return None
