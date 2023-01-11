"""!
@package pytrader.libs.securitybase

Provides the broker client

@author Geoff S. Derber
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


@file pytrader/libs/securitybase.py
"""
# System libraries
import pandas

# 3rd Party libraries
from ibapi.contract import Contract

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import bars
from pytrader.libs import orders

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class SecurityBase():

    def __init__(self, *args, **kwargs):
        logger.debug10("Begin Function")
        logger.debug("Kwargs: %s", kwargs)
        if kwargs.get("ticker_symbol"):
            self.ticker_symbol = kwargs["ticker_symbol"]
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]

        self.bars = {}

        logger.debug10("End Function")

    def set_contract(self, primary_exchange=None, exchange="SMART"):
        """!@fn set_contract

        @param exchange
        """
        logger.debug10("Begin Function")
        contract = Contract()
        contract.symbol = self.ticker_symbol
        contract.secType = self.security_type
        contract.exchange = exchange
        contract.currency = "USD"
        logger.debug("Primary Exchange: %s", primary_exchange)
        if primary_exchange:
            contract.primaryExchange = primary_exchange

        logger.debug("Contract: %s", contract)
        self.contract = contract

        logger.debug10("End Function")

        return contract

    def update_broker_info(self):
        # result = self.__get_info_from_database()

        # logger.debug("Result: %s", result)

        # if result[0]["ibkr_exchange"] == "SMART" and result[0][
        #         "ibkr_primary_exchange"]:
        #     self.primary_exchange = result[0]["ibkr_primary_exchange"]
        #     self.set_contract(self.ticker_symbol,
        #                       self.security_type,
        #                       primary_exchange=self.primary_exchange)
        # else:
        #     self.set_contract(self.ticker_symbol, self.security_type)

        self.set_contract()
        logger.debug("Get Security Data")
        req_id = self.brokerclient.get_security_data(self.contract)
        logger.debug("Request ID: %s", req_id)
        data = self.brokerclient.get_data(req_id)
        logger.debug("Data: %s", data)

        # self.update_ipo_date()
        logger.debug10("End Function")
        return None

    def update_info(self, source=None):
        logger.debug10("Begin Function")

        if source == "broker" or source == "ibkr":
            self.update_broker_info()
        elif source == "yahoo":
            self.update_yahoo_info()
        else:
            logger.error("Source Not Selected.")

    def get_broker_info(self):
        """!
        get_broker_info
        """

        req_id = self.brokerclient.get_security_data(self.contract)
        data = self.brokerclient.get_data(req_id)
        return data

    def get_yahoo_info(self, ticker):
        yc = yahoo.YahooClient()
        yc.get_info(self.securities_type, ticker)

    def place_order(self):
        logger.debug10("Begin Function")
        order = orders.Order(order_type="market",
                             action="BUY",
                             quantity=1,
                             transmit=False,
                             brokerclient=self.brokerclient)
        logger.debug("Contract: %s", self.contract)
        logger.debug("Order:\n%s", order)
        order.place_order(self.contract)

        logger.debug10("End Function")

    def get_bars(self, bar_size):
        logger.debug("Begin Function")
        bars = self.bars[bar_size].get_bars()
        logger.debug("Bars: %s", bars)
        logger.debug("End Function")
        return self.bars[bar_size].get_bars()

    def download_bars(self,
                      bar_size="1 day",
                      duration="1 W",
                      keep_up_to_date=False):
        self.bars[bar_size] = bars.Bars(brokerclient=self.brokerclient,
                                        contract=self.contract,
                                        bar_size=bar_size,
                                        duration=duration,
                                        keep_up_to_date=keep_up_to_date)
        self.bars[bar_size].download_bars()

        logger.debug("Ticker: %s", self.ticker_symbol)
        logger.debug("Bars: %s", bars)
        return self.bars

    # def update_ipo_date(self):
    #     logger.debug10("Begin Function")
    #     result = self.__get_info_from_database()

    #     if result[0]["ibkr_exchange"] == "SMART" and result[0][
    #             "ibkr_primary_exchange"]:
    #         self.primary_exchange = result[0]["ibkr_primary_exchange"]
    #         self.set_contract(self.ticker_symbol,
    #                           self.security_type,
    #                           primary_exchange=self.primary_exchange)
    #     else:
    #         self.set_contract(self.ticker_symbol, self.security_type)

    #     logger.debug("Get Security Data")
    #     req_id = self.brokerclient.get_ipo_date(self.contract)
    #     logger.debug("Request ID: %s", req_id)
    #     data = self.brokerclient.get_data(req_id)
    #     self.brokerclient.cancel_head_timestamp(req_id)
    #     ipo_date = datetime.datetime.strptime(data, "%Y%m%d-%H:%M:%S")
    #     logger.debug("Data: %s", ipo_date)

    #     db = etf_info.EtfInfo()
    #     db.update_ibkr_ipo_date(self.ticker_symbol, ipo_date)

    #     logger.debug10("End Function")
    #     return None

    def calculate_ema(self, bar_size, span):
        self.bars[bar_size].calculate_ema(span)

    def calculate_sma(self, bar_size, span):
        self.bars[bar_size].calculate_sma(span)
