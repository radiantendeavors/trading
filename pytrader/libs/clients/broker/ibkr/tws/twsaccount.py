"""!
@package pytrader.libs.clients.broker.ibkr.tws.twsdemo

Creates the interface for connecting to Tws Demo account.

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

@file pytrader/libs/clients/broker/ibkr/tws/twsdemo.py

Creates the interface for connecting to Tws Demo account.
"""
# System Libraries
import threading

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader import CLIENT_ID
from pytrader.libs.clients.broker.abstractclient import AbstractBrokerClient
from pytrader.libs.clients.broker.ibkr.tws import TwsApiClient

from pytrader.libs.clients.broker.observers import (
    StrategyBarDataObserver, StrategyContractDataObserver, StrategyMarketDataObserver,
    StrategyOptionDataObserver, StrategyOrderDataObserver, StrategyRealTimeBarObserver)
from pytrader.libs.clients.broker.subjects import (BrokerBarData, BrokerContractData,
                                                   BrokerMarketData, BrokerOptionData,
                                                   BrokerOrderData, BrokerRealTimeBarData)

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
class TwsAccountClient(AbstractBrokerClient):
    """!
    Base Class common to all account types:
      - TwsReal
      - TwsDemo
      - IbgReal
      - IbgDemo
    """
    brokerclient = TwsApiClient()

    contract_subjects = BrokerContractData()
    bar_subjects = BrokerBarData()
    mkt_data_subjects = BrokerMarketData()
    option_subjects = BrokerOptionData()
    order_subjects = BrokerOrderData()
    rtb_subjects = BrokerRealTimeBarData()

    def __init__(self, data_queue: dict) -> None:
        """!
        Initializes the TwsDataThread class.
        """
        # Contract Subjects and Observers
        self.contract_observers = {}
        self.bar_observers = {}
        self.mkt_data_observers = {}
        self.option_observers = {}
        self.order_observers = {}
        self.rtb_observers = {}
        self.client_thread = threading.Thread(target=self.run, daemon=True)

        super().__init__(data_queue)

    def connect(self, address: str = "127.0.0.1", port: int = 0, client_id: int = CLIENT_ID):
        if port == 0:
            port = self.port
        self.brokerclient.connect(address, port, client_id)

    def start(self):
        self.client_thread.start()
        self.brokerclient.start(self.queue)

    def stop(self):
        self.brokerclient.stop()

    def cancel_order(self, order_id: int) -> None:
        """!
        Cancels a specific order.

        @param order_id: The order id to cancel.

        @return None.
        """
        self.order_subjects.cancel_order(order_id)

    def calculate_implied_volatility(self):
        logger.debug("Calculate Implied Volatility")

    def create_order(self, order_request: dict, strategy_id: str) -> None:
        """!
        Create a new order from an order request.

        @param order_request: The details of the order to create.

        @return None.
        """
        order_contract = order_request["contract"]
        new_order = order_request["order"]
        order_id = new_order.orderId

        self.order_subjects.create_order(order_contract, new_order, order_id)
        self.order_observers[strategy_id].add_order_id(order_id)

    def request_bar_history(self) -> None:
        self.bar_subjects.request_bars()
        self.bar_subjects.notify()

    def request_global_cancel(self) -> None:
        self.brokerclient.req_global_cancel()

    def request_option_details(self, strategy_id):
        tickers = self.contract_observers[strategy_id].get_tickers()
        contracts = self.contract_subjects.get_contracts()

        self.option_observers[strategy_id].add_tickers(tickers)
        self.option_subjects.add_tickers(tickers, contracts)
        self.option_subjects.request_option_details()
        self.option_subjects.notify()

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

    def set_strategies(self, strategy_list: list) -> None:
        """!
        Sets the subject and observers for each strategy.

        @param strategy_list: List of strategies to use.

        @return None
        """
        for strategy in strategy_list:
            # Add Bar Observers
            self.bar_observers[strategy] = StrategyBarDataObserver(self.data_queue[strategy])
            self.bar_subjects.attach(self.bar_observers[strategy], self.brokerclient)

            # Add Contract Observers
            self.contract_observers[strategy] = StrategyContractDataObserver(
                self.data_queue[strategy])
            self.contract_subjects.attach(self.contract_observers[strategy], self.brokerclient)

            # Add MarketData Observers
            self.mkt_data_observers[strategy] = StrategyMarketDataObserver(
                self.data_queue[strategy])
            self.mkt_data_subjects.attach(self.mkt_data_observers[strategy], self.brokerclient)

            # Add Option Detail Observers
            self.option_observers[strategy] = StrategyOptionDataObserver(self.data_queue[strategy])
            self.option_subjects.attach(self.option_observers[strategy], self.brokerclient)

            # Add Option Detail Observers
            self.order_observers[strategy] = StrategyOrderDataObserver(self.data_queue[strategy])
            self.order_subjects.attach(self.order_observers[strategy], self.brokerclient)

            # Add Real Time Bar Observers
            self.rtb_observers[strategy] = StrategyRealTimeBarObserver(self.data_queue[strategy])
            self.rtb_subjects.attach(self.rtb_observers[strategy], self.brokerclient)

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

    def set_contracts(self, contracts: dict, strategy_id: str):
        for ticker, contract_ in contracts.items():
            self.contract_subjects.request_contract_data(ticker, contract_)

        # We do this after requesting contract detail, so we can check if the ticker has a valid
        # contract.
        valid_tickers = self.contract_subjects.get_tickers()
        tickers = set(valid_tickers).intersection(list(contracts))

        self.contract_observers[strategy_id].add_tickers(tickers)

        logger.debug("Contracts: %s", valid_tickers)
        self.contract_subjects.notify()
