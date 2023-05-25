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
import string
import time

# 3rd Party libraries
from ibapi import contract

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients import polygon

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)

POLYGON_SLEEP_TIME = 15


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Contracts():

    def __init__(self, *args, **kwargs):
        logger.debug10("Begin Function")

        ## Command Queue
        self.cmd_queue = args[0]

        ## Contracts
        self.contracts = {}

        ## List of Securities
        self.securities_list = []

        ## Security Type
        self.securities_type = None

        if args[1] and len(args) > 1:
            self.securities_type = args[1]
        elif kwargs.get("securities_type"):
            self.securities_type = kwargs["securities_type"]

        if args[2] and len(args) > 2:
            self.securities_list = args[2]
        elif kwargs.get("securities_list"):
            self.securities_list = kwargs["securities_list"]

    def update_history(self, source, bar_size, duration):
        logger.debug10("Begin Function")
        logger.debug("Securities List: %s", self.securities_list)

        if source == "broker":
            self._update_history_broker(bar_size, duration)
        else:
            self._update_history_broker(bar_size, duration)

        logger.debug10("End Function")
        return None

    def update_info(self, source: str = "", *args, **kwargs):
        logger.debug10("Begin Function")
        logger.debug("Source: %s", source)

        # Normally, I like to have these sorted by name.
        # Here, we want polygon.io to always be first if nothing is specified.
        # This is because polygon.io is the baseline for ticker lists.
        func_map = {
            "polygon": self._update_info_polygon,
            "broker": self._update_info_broker
        }

        if source:
            func = func_map.get(source)
            func(args, kwargs)
        else:
            for key in func_map.keys():
                func = func_map.key
                func(args, kwargs)

        logger.debug10("End Function")
        return None

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _create_contract(self,
                         ticker,
                         sec_type: str = "STK",
                         exchange: str = "SMART",
                         currency: str = "USD",
                         expiry: str = "",
                         strike: float = 0.0,
                         right: str = ""):
        """!
        Creates a contract
        """
        contract_ = contract.Contract()
        contract_.symbol = ticker
        contract_.secType = sec_type
        contract_.exchange = exchange
        contract_.currency = currency

        if expiry != "":
            contract_.lastTradeDateOrContractMonth = expiry
            contract_.multiplier = "100"

        if float(strike) > 0.0:
            contract_.strike = strike

        if right != "":
            contract_.right = right

        return contract_

    def _create_contracts(self):
        for item in self.securities_list:
            self.contracts[item] = self._create_contract(item)

        logger.debug("Contracts: %s", self.contracts)

    def _get_polygon_ticker_list(self, ticker_type):
        logger.debug10("Begin Function")
        client = polygon.PolygonClient()
        tickers = []
        i = 0
        alphabet = string.ascii_uppercase

        while i < len(alphabet):
            j = 0

            while j < len(alphabet):
                k = 0

                while k < len(alphabet):
                    l = 0

                    while l < len(alphabet):
                        if j == 0 and k == 0 and l == 0:
                            begin = alphabet[i]
                            end = alphabet[i] + alphabet[j] + alphabet[
                                k] + alphabet[l] + "ZZZZZZ"
                        elif k == 0 and l == 0:
                            begin = alphabet[i] + alphabet[j]
                            end = alphabet[i] + alphabet[j] + alphabet[
                                k] + alphabet[l] + "ZZZZZZ"
                        elif l == 0:
                            begin = alphabet[i] + alphabet[j] + alphabet[k]
                            end = alphabet[i] + alphabet[j] + alphabet[
                                k] + alphabet[l] + "ZZZZZZ"
                        else:
                            begin = alphabet[i] + alphabet[j] + alphabet[
                                k] + alphabet[l]
                            end = alphabet[i] + alphabet[j] + alphabet[
                                k] + alphabet[l] + "ZZZZZZ"

                        logger.debug3("1st Letter: %s", begin)
                        logger.debug3("2nd Letter: %s", end)

                        if ticker_type == "INDEX":
                            begin = "I:" + begin
                            end = "I:" + end
                            ticker_list = client.list_tickers(ticker_gte=begin,
                                                              ticker_lte=end,
                                                              limit=1000,
                                                              market="indices")
                        else:
                            ticker_list = client.list_tickers(ticker_gte=begin,
                                                              ticker_lte=end,
                                                              limit=1000,
                                                              type=ticker_type)
                            logger.debug4("Ticker List: %s", ticker_list)

                        for item in ticker_list:
                            tickers.append(item)
                            logger.debug3("Ticker Item: %s", item)

                        time.sleep(POLYGON_SLEEP_TIME)

                        l += 1

                    k += 1

                j += 1

            i += 1

        logger.debug10("End Function")
        return tickers

    def _get_polygon_ticker_types(self,
                                  asset_class=None,
                                  locale=None,
                                  params=None,
                                  raw=False):
        logger.debug10("Begin Function")

        polygon_client = polygon.PolygonClient()
        ticker_types = polygon_client.get_ticker_types(asset_class, locale,
                                                       params, raw)

        return ticker_types

    def _update_history_broker(self, bar_size=None, duration=None):
        logger.debug10("Begin Function")
        logger.debug("Type: %s", self.securities_type)
        for ticker in self.securities_list:
            investment = security.Security(security_type=self.securities_type,
                                           ticker_symbol=ticker["ticker"],
                                           bar_sizes=bar_size,
                                           duration=duration,
                                           brokerclient=self.brokerclient)
            investment.update_history()
        logger.debug10("End Function")

    def _update_info_broker(self):
        logger.debug10("Begin Function")
        if self.securities_list:
            logger.debug("Securities List: %s", self.securities_list)
        else:
            logger.error("Not impletemented yet")

        self._create_contract()
        self._send_contracts()

        logger.debug10("End Function")

    def _update_info_polygon(self, *args, **kwargs):
        asset_classes = args[0][0]
        locale = args[0][1]

        tickers = []

        logger.debug10("Begin Function")

        logger.debug2("Asset Class: %s", asset_classes)
        logger.debug2("Locale: %s", locale)

        for asset_class in asset_classes:
            if asset_class == "stocks":
                ticker_types = self._get_polygon_ticker_types(
                    asset_class, locale)
                logger.debug("Ticker Type: %s", ticker_types)
                time.sleep(POLYGON_SLEEP_TIME)

                for item in ticker_types:
                    logger.debug("Code: %s", item.code)
                    logger.debug("Description: %s", item.description)

                    tickers.append(self._get_polygon_ticker_list(item.code))

            elif asset_class == "indices":
                tickers.append(self._get_polygon_ticker_list("INDEX"))

        for item in tickers:
            logger.debug("Ticker: %s Name: %s Market: %s Type: %s",
                         item.ticker, item.name, item.market, item.type)

        logger.debug10("End Function")

    def _send_contracts(self, contracts: dict = {}):
        if contracts:
            contracts_to_send = contracts
        else:
            contracts_to_send = self.contracts

        if contracts is False:
            logger.error("Contracts Not Set")

        message = {"set": {"tickers": contracts_to_send}}
        self.cmd_queue.put(message)
