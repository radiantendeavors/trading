"""!@package pytrader.libs.applications.broker.ibkr.tws

The main user interface for the trading program.

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

@file pytrader/libs/applications/broker/ibkr/tws/__init__.py
"""
# System Libraries
import datetime
import threading
from multiprocessing import Queue

# 3rd Party Libraries
from ibapi.contract import Contract
from ibapi.order import Order

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.applications.broker.common import BrokerDataThread
from pytrader.libs.applications.broker.common import orders
# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class TwsDataThread(BrokerDataThread):
    """!
    Serves as the client interface for Interactive Brokers
    """

    def __init__(self, *args, **kwargs):
        """!
        Initializes the TwsDataThread class.
        """

        ## Dictionary containing all active contracts.
        self.contracts = {}

        ## List containing all active bar sizes.
        self.bar_sizes = []

        ## Dictionary to match request ids to contracts for historical bars.
        self.historical_bar_ids = {}

        ## Dictionary to match request ids to contracts for real time bars.
        self.rtb_ids = {}

        ## Dictionary to match request ids to contracts for real time market data.
        self.rtmd_ids = {}

        super().__init__(*args, **kwargs)

    def cancel_order(self, order_id: int):
        """!
        Cancels a specific order.

        @param order_id: The order id to cancel.

        @return None.
        """
        self.brokerclient.cancel_order(order_id)

    def create_order(self, order_request: dict):
        """!
        Create a new order from an order request.

        @param order_request: The details of the order to create.

        @return None.
        """
        order_contract = order_request["contract"]
        new_order = order_request["order"]

        self.brokerclient.place_order(order_contract, new_order, new_order.orderId)

    def request_bar_history(self):
        for contract_ in list(self.contracts.values()):
            for size in self.bar_sizes:
                if size != "rtb":
                    self._retrieve_bar_history(contract_, size)

    def request_option_details(self):
        for ticker, contract_ in self.contracts.items():
            req_id = self.brokerclient.req_sec_def_opt_params(contract_)
            option_details = self.brokerclient.get_data(req_id)
            #logger.debug2("Requesting Option Details  for Ticker: %s", ticker)

            message = {"option_details": {"ticker": ticker, "details": option_details}}
            logger.debug9("Option Details: %s", message)
            self.data_queue.put(message)

    def request_real_time_bars(self):
        for ticker, contract_ in self.contracts.items():

            if ticker not in self.rtb_ids.values():
                logger.debug2("Requesting Real Time Bars for Ticker: %s", ticker)
                req_id = self.brokerclient.req_real_time_bars(contract_)
                self.rtb_ids[req_id] = ticker

    def request_market_data(self):
        for ticker, contract_ in self.contracts.items():
            if ticker not in self.rtmd_ids.values():
                logger.debug2("Requesting Market Data for Ticker: %s", ticker)
                req_id = self.brokerclient.req_market_data(contract_)
                self.rtmd_ids[req_id] = ticker

    def send_market_data_ticks(self, market_data: dict):
        req_id = list(market_data.keys())[0]
        ticker = self.rtmd_ids[req_id]
        contract_ = self.contracts[ticker]
        self.send_ticks(contract_, market_data[req_id])

    def send_order_status(self, order_status: dict):
        logger.debug9("Order Status: %s", order_status)
        self.data_queue.put(order_status)

    def send_real_time_bars(self, real_time_bar: dict):
        # There should really only be one key.
        req_id = list(real_time_bar.keys())[0]
        ticker = self.rtb_ids[req_id]
        contract_ = self.contracts[ticker]

        rtb = real_time_bar[req_id]

        bar_datetime = datetime.datetime.fromtimestamp(rtb[0]).strftime('%Y%m%d %H:%M:%S')
        bar_datetime_str = str(bar_datetime) + " EST"

        rtb[0] = bar_datetime_str
        rtb[5] = int(rtb[5])
        rtb[6] = float(rtb[6])
        self.send_bars(contract_, "real_time_bars", "rtb", rtb)

    def set_bar_sizes(self, bar_sizes: list):
        """!
        Sets bar sizes

        @param bar_sizes: Bar sizes to use

        @return None
        """
        # We use keys here because we do not need the entire key, value pair
        self.bar_sizes = bar_sizes

    def set_contracts(self, contracts: dict):
        for ticker, contract_ in contracts.items():
            logger.debug2("Requesting Contract Details for contract: %s", ticker)

            req_id = self.brokerclient.req_contract_details(contract_)
            contract_details = self.brokerclient.get_data(req_id)

            if isinstance(contract_details, (dict, set)):
                logger.error("Failed to obtain contract details for %s", ticker)
                logger.error("Contract: %s", contract_details)
            else:
                new_contract = contract_details.contract
                if new_contract.localSymbol not in list(self.contracts.keys()):
                    self.contracts[new_contract.localSymbol] = new_contract

        msg = {"contracts": self.contracts}
        logger.debug9("Sending New Contracts: %s", msg)
        self.data_queue.put(msg)

    # ==============================================================================================
    #
    # Internal Use only functions.  These should not be used outside the class.
    #
    # ==============================================================================================
    def _retrieve_bar_history(self, contract_: Contract, size: str):
        if size == "rtb":
            logger.error("Invalid Bar Size for History")
        else:
            duration = self._set_duration(size)

            if self.brokerclient:
                self._retreive_broker_bar_history(contract_, size, duration)
            else:
                raise NotImplementedError

    def _retreive_broker_bar_history(self, contract_: Contract, size: str, duration: str):
        if contract_.localSymbol not in list(self.historical_bar_ids.keys()):
            self.historical_bar_ids[contract_.localSymbol] = {}

        if size not in list(self.historical_bar_ids[contract_.localSymbol].keys()):
            new_bar_list = []

            if duration == "all":
                logger.debug8("Getting all history")

            else:
                req_id = self.brokerclient.req_historical_data(contract_,
                                                               size,
                                                               duration_str=duration)

            # Bar List is a list of ibapi class Bar.
            bar_list = self.brokerclient.get_data(req_id)

            logger.debug9("Bar List: %s", bar_list)

            # This is done to convert the Bar Class into a list of elements.
            for ohlc_bar in bar_list:
                logger.debug9("Bar: %s", ohlc_bar)

                new_bar_list.append([
                    ohlc_bar.date, ohlc_bar.open, ohlc_bar.high, ohlc_bar.low, ohlc_bar.close,
                    float(ohlc_bar.volume), ohlc_bar.wap, ohlc_bar.barCount
                ])

            self.send_bars(contract_, "bars", size, new_bar_list)
            self.historical_bar_ids[contract_.localSymbol][size] = req_id

    def _set_duration(self, size: str):
        logger.debug5("Setting Duration for Bar Size: %s", size)
        if size == "1 month":
            duration = "2 Y"
        elif size == "1 week":
            duration = "1 Y"
        elif size == "1 day":
            duration = "1 Y"
        elif size == "1 hour":
            duration = "7 W"
        elif size == "30 mins":
            duration = "4 W"
        elif size == "15 mins":
            duration = "10 D"
        elif size == "5 mins":
            duration = "4 D"
        elif size in ["15 secs", "30 secs", "1 min"]:
            duration = "2 D"
        logger.debug9("Duration Set to %s", duration)

        return duration
