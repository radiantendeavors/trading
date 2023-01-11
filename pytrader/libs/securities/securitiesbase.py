"""!
@package pytrader.libs.securities.securitiesbase

Provides the Base Class for Securities

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


@file pytrader/libs/securities/securitiesbase.py
"""
# System libraries
import random
import string
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients import nasdaq, polygon, yahoo
from pytrader.libs.securities import security
# from pytrader.libs import indexes
# from pytrader.libs.securities import etfs, stocks
from pytrader.libs.clients.mysql import etf_info, index_info, stock_info

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
class SecuritiesBase():

    def __init__(self, *args, **kwargs):
        self.securities_list = {}
        if kwargs.get("client_id"):
            self.client_id = kwargs["client_id"]
        else:
            self.client_id = 0

        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]
            logger.debug("BrokerClient: %s", self.brokerclient)

    def __update_info_broker(self):
        logger.debug10("Begin Function")

        for item in self.securities_list:
            logger.debug2("Item: %s", item)
            logger.debug3("Investment Type: %s", self.securities_type)
            investment = security.Security(security_type=self.securities_type,
                                           ticker_symbol=item["ticker"],
                                           brokerclient=self.brokerclient)

            logger.debug("Security: %s", investment)
            investment.update_info(source="ibkr")

        logger.debug10("End Function")
        return None

    def __update_info_nasdaq(self):
        logger.debug10("Begin Function")
        client = nasdaq.NasdaqClient(investments=self.securities_type)
        client.download_list()
        logger.debug10("End Function")
        return None

    def __update_info_polygon(self):
        logger.debug10("Begin Function")

        if self.securities_type == "etfs":
            ticker_type = "etf"
        elif self.securities_type == "stocks":
            ticker_type = "cs"
        else:
            logger.error("Invalid ticker type: %s", self.securities_type)

        client = polygon.PolygonClient()
        tickers = []
        i = 0
        alphabet = string.ascii_uppercase
        while i < len(alphabet) - 2:
            logger.debug3("1st Letter: %s", alphabet[i])
            logger.debug3("2nd Letter: %s", alphabet[i + 1])

            tickers.append(
                client.list_tickers(ticker_gte=alphabet[i],
                                    ticker_lt=alphabet[i + 2],
                                    limit=1000,
                                    type=ticker_type))
            i += 2
            time.sleep(15)

        for item in tickers:
            logger.debug("Tickers: %s", item)

        logger.debug10("End Function")

    def __update_info_yahoo(self):
        logger.debug10("Begin Function")
        for ticker in self.securities_list:
            logger.debug("Ticker: %s", ticker["yahoo_symbol"])

            if ticker["yahoo_symbol"]:
                yahoo_symbol = ticker["yahoo_symbol"]
            else:
                yahoo_symbol = ticker["ticker"]

            investment = security.Security(security_type=self.securities_type,
                                           ticker_symbol=yahoo_symbol)

            investment.update_info("yahoo")
        logger.debug10("End Function")
        return None

    def __update_history_yahoo(self, bar_size, period):
        logger.debug10("Begin Function")
        for ticker in self.securities_list:
            logger.debug("Ticker: %s", ticker["yahoo_symbol"])
            if ticker["yahoo_symbol"]:
                yc = yahoo.YahooClient()
                yc.get_bar_history(self.securities_type,
                                   ticker["ticker"],
                                   ticker["yahoo_symbol"],
                                   interval=bar_size,
                                   period=period)
            if ticker != self.securities_list[-1]:
                time.sleep(random.randint(min_sleeptime, max_sleeptime))

        logger.debug10("End Function")
        return None

    def update_history(self, source, bar_size, period, securities_list=None):
        logger.debug10("Begin Function")
        if self.securities_list:
            logger.debug("Securities List: %s", self.securities_list)
        else:
            self.get_list(securities_list)

        logger.debug("Securities List: %s", self.securities_list)

        if source == "broker":
            self.__update_history_broker(bar_size, period)
        elif source == "yahoo":
            self.__update_history_yahoo(bar_size, period)
        else:
            self.__update_history_broker(bar_size, period)
            self.__update_history_yahoo(bar_size, period)

        logger.debug("End Function")
        return None

    def update_info(self, source=None, securities_list=None):
        logger.debug10("Begin Function")
        logger.debug("Source: %s", source)

        if self.securities_list:
            logger.debug("Securities List: %s", self.securities_list)
        else:
            self.get_list(securities_list)

        if source == "broker":
            self.__update_info_broker()
        elif source == "nasdaq":
            self.__update_info_nasdaq()
        elif source == "polygon":
            self.__update_info_polygon()
        elif source == "yahoo":
            self.__update_info_yahoo()
        else:
            self.__update_info_broker
            self.__update_info_nasdaq()
            self.__update_info_yahoo()

        logger.debug("End Function")
        return None
