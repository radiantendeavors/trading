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

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.applications.broker.common import BrokerDataThread
from pytrader.libs.applications.broker.ibkr.tws.observers import (
    StrategyBarDataObserver, StrategyContractDataObserver, StrategyMarketDataObserver,
    StrategyOptionDataObserver, StrategyOrderDataObserver, StrategyRealTimeBarObserver)
from pytrader.libs.applications.broker.ibkr.tws.subjects import (BrokerBarData, BrokerContractData,
                                                                 BrokerMarketData, BrokerOptionData,
                                                                 BrokerOrderData,
                                                                 BrokerRealTimeBarData)
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
        # Contract Subjects and Observers
        self.contract_subjects = BrokerContractData()
        self.contract_observers = {}

        self.bar_subjects = BrokerBarData()
        self.bar_observers = {}

        self.mkt_data_subjects = BrokerMarketData()
        self.mkt_data_observers = {}

        self.option_subjects = BrokerOptionData()
        self.option_observers = {}

        self.order_subjects = BrokerOrderData()
        self.order_observers = {}

        self.rtb_subjects = BrokerRealTimeBarData()
        self.rtb_observers = {}

        super().__init__(*args, **kwargs)

    def cancel_order(self, order_id: int):
        """!
        Cancels a specific order.

        @param order_id: The order id to cancel.

        @return None.
        """
        self.order_subjects.cancel_order(order_id)

    def create_order(self, order_request: dict, strategy_id: str):
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

    def request_bar_history(self):
        self.bar_subjects.request_bars()
        self.bar_subjects.notify()

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

    def set_strategies(self, strategy_list: list):
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
        tickers = set(valid_tickers).intersection(list(contracts.keys()))

        self.contract_observers[strategy_id].add_tickers(tickers)
        self.contract_subjects.notify()
