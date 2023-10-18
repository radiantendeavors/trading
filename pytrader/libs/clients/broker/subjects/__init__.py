"""!@package pytrader.libs.applications.broker.ibkr.tws.subjects

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

@file pytrader/libs/applications/broker/ibkr/tws/subjects.py
"""
import datetime

from ibapi.contract import Contract, ContractDetails
from ibapi.order import Order

from pytrader.libs.events import (BarData, ContractData,
                                  ContractHistoryBeginDate,
                                  ContractOptionParametrsData, MarketData,
                                  OrderData, OrderIdData, RealTimeBarData)
from pytrader.libs.system import logging

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
class BrokerBarData(BarData):
    """!
    Broker specific bar data subject.
    """

    def request_bars(self):
        """!
        Request bars
        """
        for contract_ in list(self.contracts.values()):
            if contract_.localSymbol not in list(self.ohlc_bars):
                self.ohlc_bars[contract_.localSymbol] = {}

            for bar_size in self.bar_sizes:
                if bar_size not in list(self.ohlc_bars[contract_.localSymbol]):
                    self._retrieve_bar_history(contract_, bar_size)

    # ==============================================================================================
    #
    # Internal Use only functions.  These should not be used outside the class.
    #
    # ==============================================================================================
    def _retrieve_bar_history(self, contract_: Contract, bar_size: str):
        if contract_.secType == "OPT" and bar_size == "1 day":
            logger.debug9("Option Daily Bar, skipping")
        else:
            duration = self._set_duration(bar_size)

            if self.brokerclient:
                self._retreive_broker_bar_history(contract_, bar_size, duration)
            else:
                raise NotImplementedError

    def _retreive_broker_bar_history(self, contract_: Contract, bar_size: str, duration: str):
        new_bar_list = []

        if duration == "all":
            logger.debug8("Getting all history")
        else:
            req_id = self.brokerclient.req_historical_data(contract_,
                                                           bar_size,
                                                           duration_str=duration)

        # Bar List is a list of ibapi class Bar.
        bar_list = self.brokerclient.get_data(req_id)
        logger.debug9("Bar List: %s", bar_list)
        logger.debug2("%s: %s Bars received", contract_.localSymbol, bar_size)

        # This is done to convert the Bar Class into a list of elements.
        for ohlc_bar in bar_list:
            logger.debug9("Bar: %s", ohlc_bar)

            new_bar_list.append([
                ohlc_bar.date, ohlc_bar.open, ohlc_bar.high, ohlc_bar.low, ohlc_bar.close,
                float(ohlc_bar.volume), ohlc_bar.wap, ohlc_bar.barCount
            ])

        self.ohlc_bars[contract_.localSymbol][bar_size] = new_bar_list

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
        elif size in ["5 secs", "15 secs", "30 secs", "1 min"]:
            duration = "2 D"
        logger.debug9("Duration Set to %s", duration)

        return duration


class BrokerContractData(ContractData):
    """!
    Contract Data Subject
    """

    def set_contract_details(self, req_id: int, contract_details: ContractDetails | str) -> None:
        """!
        Sets the contract details, then notifies the observers.

        @param req_id: The req_id of the contract details received.
        @param contract_details: The contract details received.

        @return None.
        """
        self.req_id = req_id
        self.contracts[req_id] = contract_details
        self.notify()

        #self.contracts.pop(req_id, None)
        #self.req_ids.pop(req_id, None)


class BrokerContractHistoryBeginDate(ContractHistoryBeginDate):
    """!
    Contract History Begin Subject
    """

    def set_history_begin_date(self, req_id: int, history_begin_date: str) -> None:
        """!
        Sets the history begin date, then notifies the observers.

        @param req_id: The req_id of the history begin date received.
        @param history_begin_date:

        @return None
        """
        self.req_id = req_id
        self.history_begin_date[req_id] = history_begin_date
        self.notify()
        self.history_begin_date.pop(req_id, None)
        self.history_begin_ids.pop(req_id, None)


class BrokerContractOptionParametersData(ContractOptionParametrsData):
    """!
    Contract Option Parameters Subject
    """

    def set_option_parameter(self, req_id: int, option_parameters: dict) -> None:
        """!
        Sets the option parameters for the contract, then notifies the observers.

        @param req_id: The req_id of the option parameters received.
        @param option_parameters: The option parameters received.

        @return None
        """
        self.req_id = req_id
        self.option_parameters[req_id] = option_parameters
        self.notify()

        # Shit! I thought I was being clever by removing this data when no longer needed.
        # Unfortunately, it's sometimes needed for a little longer.
        #self.option_parameters.pop(req_id, None)
        #self.req_ids.pop(req_id, None)


class BrokerMarketData(MarketData):
    """!
    Market Data Subject
    """

    def request_market_data(self) -> None:
        """!
        Requests market data.

        @return None
        """
        for ticker, contract_ in self.contracts.items():
            if ticker not in self.rtmd_ids.values():
                logger.debug2("Requesting Market Data for Ticker: %s", ticker)
                req_id = self.brokerclient.req_market_data(contract_)
                self.rtmd_ids[req_id] = ticker

    def send_market_data_ticks(self, market_data: dict) -> None:
        """!
        Sets the market data information, then notifies the observers.

        @param market_data:

        @return None
        """
        req_id = list(market_data)[0]
        self.ticker = self.rtmd_ids[req_id]
        self.market_data = market_data[req_id]
        self.notify()


class BrokerOrderData(OrderData):
    """!
    Broker Order Data Subject
    """

    def cancel_order(self, order_id: int) -> None:
        """!
        Cancels specified order.

        @param order_id: The order_id of the order to cancel.

        @retur None
        """
        if order_id in self.valid_order_ids:
            self.brokerclient.cancel_order(order_id)

    def create_order(self, order_contract: Contract, new_order: Order, order_id: int) -> None:
        """!
        Create a new order from an order request.

        @param order_request: The details of the order to create.

        @return None.
        """
        self.valid_order_ids.append(order_id)
        self.brokerclient.place_order(order_contract, new_order, order_id)

    def send_order_status(self, order_status: dict) -> None:
        """!
        Updates the order status, and notifies the observers.

        @param order_status:

        @return None
        """
        self.order_id = list(order_status)[0]
        self.order_status = order_status
        status = order_status[self.order_id]["status"]

        if status in ["Filled", "Cancelled", "ApiCancelled", "TWS_CLOSED"]:
            if self.order_id in self.valid_order_ids:
                self.valid_order_ids.remove(self.order_id)

        self.notify()


class BrokerOrderIdData(OrderIdData):
    """!
    Broker Order Id Subject
    """

    def send_order_id(self, order_id: int) -> None:
        """!
        Updates the order id, and notifies the observers.

        @param order_id:

        @return None
        """
        self.order_id = order_id
        self.notify()


class BrokerRealTimeBarData(RealTimeBarData):
    """!
    Broker Real Time Bar Data subject
    """

    def request_real_time_bars(self) -> None:
        """!
        Requets real time bars.

        @return None.
        """
        for ticker, contract_ in self.contracts.items():
            if ticker not in self.rtb_ids.values():
                logger.debug2("Requesting Real Time Bars for Ticker: %s", ticker)
                req_id = self.brokerclient.req_real_time_bars(contract_)
                self.rtb_ids[req_id] = ticker

    def send_real_time_bars(self, real_time_bar: dict) -> None:
        """!
        Updates the real time bar information, and notifies the observers.

        @param real_time_bar:

        @return None
        """
        # There should really only be one key.
        req_id = list(real_time_bar)[0]
        self.ticker = self.rtb_ids[req_id]

        rtb = real_time_bar[req_id]
        bar_datetime = datetime.datetime.fromtimestamp(rtb[0]).strftime('%Y%m%d %H:%M:%S')
        bar_datetime_str = str(bar_datetime) + " EST"

        rtb[0] = bar_datetime_str
        rtb[5] = int(rtb[5])
        rtb[6] = float(rtb[6])
        self.ohlc_bar = rtb
        self.notify()
