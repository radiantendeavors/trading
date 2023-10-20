"""!
@package pytrader.libs.clients.broker.ibkr.tws.twsaccount

Creates the base class for the different TWS API acounts.

@author G S Derber
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

@file pytrader/libs/clients/broker/ibkr/tws/twsaccount.py

Creates the base class for the different TWS API acounts.
"""
from typing import Optional

from ibapi.contract import Contract

from pytrader.libs.clients.broker.abstractclient import AbstractBrokerClient
from pytrader.libs.clients.broker.ibkr.tws.client import TwsApiClient
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
class TwsAccountClient(AbstractBrokerClient):
    """!
    Base Class common to all account types:
      - TwsReal
      - TwsDemo
      - IbgReal
      - IbgDemo
    """

    def __init__(self, data_queue: dict) -> None:
        """!
        Initializes the TwsDataThread class.
        """
        #
        self.brokerclient = TwsApiClient()

        # Contract Subjects and Observers
        self.req_id = 0

        super().__init__(data_queue)

    def connect(self, address: str, client_id: int, port: Optional[int] = 0) -> None:
        """!
        Connects to the broker.

        @param address: The broker ip or url.
        @param client_id:
        @param port:

        @return None
        """
        if port == 0:
            port = self.port
        self.brokerclient.connect(address, port, client_id)

    def start(self, role: str, strategies: Optional[list] = None):
        self.brokerclient.start(role, self.data_queue, self.queue, strategies)

    def stop(self):
        self.brokerclient.stop()

    def cancel_order(self, order_id: int) -> None:
        """!
        Cancels a specific order.

        @param order_id: The order id to cancel.

        @return None.
        """
        self.order_subjects.cancel_order(order_id)

    def calculate_implied_volatility(self,
                                     req_id: int,
                                     contract: Contract,
                                     option_price: float,
                                     underlying_price: float,
                                     implied_volatility_options: Optional[list] = None) -> None:
        logger.debug("Calculate Implied Volatility")

    def calculate_option_price(self, req_id: int, contract: Contract, volatility: float,
                               underlying_price: float) -> None:
        logger.debug("Calculate Option Price")

    def create_order(self, order_request: dict, strategy_id: str) -> None:
        """!
        Create a new order from an order request.

        @param order_request: The details of the order to create.

        @return None.
        """
        order_contract = order_request["contract"]
        new_order = order_request["order"]
        order_id = new_order.orderId

        self.brokerclient.place_order(order_contract, new_order, order_id)
        self.order_observers[strategy_id].add_order_id(order_id)

    def request_bar_history(self, request: dict) -> None:
        self.req_id += 1
        contract = request["contract"]
        bar_size_setting = request["bar_size_setting"]
        end_date_time = request["end_date_time"]
        duration_str = request["duration_str"]
        what_to_show = request["what_to_show"]
        use_regular_trading_hours = request["use_regular_trading_hours"]
        format_date = request["format_date"]
        keep_up_to_date = request["keep_up_to_date"]
        self.brokerclient.req_historical_data(self.req_id, contract, bar_size_setting,
                                              end_date_time, duration_str, what_to_show,
                                              use_regular_trading_hours, format_date,
                                              keep_up_to_date)

    def request_contract_details(self, request: dict):
        ticker = list(request)[0]
        contract = request[ticker]
        self.req_id += 1
        logger.debug9("Contract: %s", contract)
        self.brokerclient.add_contract_details_ticker(self.req_id, ticker)
        self.brokerclient.req_contract_details(self.req_id, contract)

    def request_global_cancel(self) -> None:
        self.brokerclient.req_global_cancel()

    def request_history_begin_date(self, contract: Contract) -> None:
        self.req_id += 1
        self.brokerclient.add_history_begin_ticker(self.req_id, contract.localSymbol)
        self.brokerclient.req_head_timestamp(self.req_id, contract)

    def request_option_details(self, contract: Contract) -> None:
        self.req_id += 1
        logger.debug("Contract: %s", contract)
        self.brokerclient.add_contract_option_params_ticker(self.req_id, contract.localSymbol)
        self.brokerclient.req_sec_def_opt_params(self.req_id, contract)

    def request_real_time_bars(self, strategy_id):
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()

        self.rtb_observers[strategy_id].add_tickers(tickers)
        self.rtb_subjects.add_tickers(tickers, contracts)
        self.rtb_subjects.request_real_time_bars()

    def request_market_data(self, strategy_id):
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()

        self.mkt_data_observers[strategy_id].add_tickers(tickers)
        self.mkt_data_subjects.add_tickers(tickers, contracts)
        self.mkt_data_subjects.request_market_data()

    def send_market_data_ticks(self, market_data: dict):
        self.mkt_data_subjects.send_market_data_ticks(market_data)

    def send_order_status(self, order_status: dict):
        self.order_subjects.send_order_status(order_status)

    def send_real_time_bars(self, real_time_bar: dict):
        self.rtb_subjects.send_real_time_bars(real_time_bar)

    def set_contract_details(self, contract_details: dict):
        self.contract_subjects.set_contract_details(contract_details)

    def set_bar_sizes(self, bar_sizes: list, strategy_id: str):
        """!
        Sets bar sizes

        @param bar_sizes: Bar sizes to use

        @return None
        """
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()
        self.bar_subjects.add_bar_sizes(tickers, contracts, bar_sizes)
        self.bar_observers[strategy_id].add_ticker_bar_sizes(tickers, bar_sizes)
