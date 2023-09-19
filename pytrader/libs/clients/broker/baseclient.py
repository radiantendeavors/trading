"""!
@package pytrader.libs.clients.broker.baseclient

Creates common methods for all brokers.

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

@file pytrader/libs/clients/broker/baseclient.py

Creates common methods for all brokers.
"""
# System Libraries
from queue import Queue

# Application Libraries
from pytrader.libs.clients.broker.observers import (
    BrokerOrderIdObserver, DownloaderBarDataObserver,
    DownloaderContractDataObserver, DownloaderContractHistoryBeginObserver,
    DownloaderMarketDataObserver, DownloaderOrderDataObserver,
    DownloaderRealTimeBarObserver, MainOrderIdObserver,
    StrategyMarketDataObserver, StrategyOrderDataObserver,
    StrategyRealTimeBarObserver)
from pytrader.libs.clients.broker.subjects import (
    BrokerBarData, BrokerContractData, BrokerContractHistoryBeginDate,
    BrokerMarketData, BrokerOrderData, BrokerOrderIdData,
    BrokerRealTimeBarData)
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
class BaseBroker():
    """!
    Base Broker Class.
    """
    # Subjects
    bar_subjects = BrokerBarData()
    contract_subjects = BrokerContractData()
    contract_history_begin_subjects = BrokerContractHistoryBeginDate()
    mkt_data_subjects = BrokerMarketData()
    order_id_subjects = BrokerOrderIdData()
    order_subjects = BrokerOrderData()
    rtb_subjects = BrokerRealTimeBarData()

    # Observers
    contract_observers = {}
    contract_history_begin_observers = {}
    bar_observers = {}
    mkt_data_observers = {}
    order_observers = {}
    order_id_observers = {}
    rtb_observers = {}
    data_queue = {}

    def set_data_queue(self, data_queue: dict) -> None:
        """!
        Sets the Data Queue.
        """
        self.data_queue = data_queue

    def config_broker_observers(self, broker_id: str, queue: Queue) -> None:
        """!
        Configures the brokers observers.

        @param broker_id: The name of the broker.
        @param queue: The message queue.

        @returun None.
        """
        self.order_id_observers[broker_id] = BrokerOrderIdObserver(queue)
        self.order_id_subjects.attach(self.order_id_observers[broker_id])

    def config_downloader_observers(self) -> None:
        """!
        Sets the subject and observers for each strategy.

        @param strategy_list: List of strategies to use.

        @return None
        """
        # Add Bar Observers
        self.bar_observers["downloader"] = DownloaderBarDataObserver(self.data_queue["downloader"])
        self.bar_subjects.attach(self.bar_observers["downloader"])

        # Add Contract Observers
        self.contract_observers["downloader"] = DownloaderContractDataObserver(
            self.data_queue["downloader"])
        self.contract_subjects.attach(self.contract_observers["downloader"])

        self.contract_history_begin_observers[
            "downloader"] = DownloaderContractHistoryBeginObserver(self.data_queue["downloader"])
        self.contract_history_begin_subjects.attach(
            self.contract_history_begin_observers["downloader"])

        # # Add Order Observers
        # self.order_observers["downloader"] = DownloaderOrderDataObserver(
        #     self.data_queue["downloader"])
        # self.order_subjects.attach(self.order_observers["downloader"], self.brokerclient)

        # # Add Market Data Observers
        # self.mkt_data_observers["downloader"] = DownloaderMarketDataObserver(
        #     self.data_queue["downloader"])
        # self.mkt_data_subjects.attach(self.mkt_data_observers["downloader"], self.brokerclient)

        # # Add Real Time Bar Observers
        # self.rtb_observers["downloader"] = DownloaderRealTimeBarObserver(
        #     self.data_queue["downloader"])
        # self.rtb_subjects.attach(self.rtb_observers["downloader"], self.brokerclient)

    def config_main_observers(self) -> None:
        """!
        Configures the brokers observers.

        @param broker_id: The name of the broker.

        @returun None.
        """
        self.order_id_observers["main"] = MainOrderIdObserver(self.data_queue["main"])
        self.order_id_subjects.attach(self.order_id_observers["main"])

    def config_strategy_observers(self, strategy_list: list) -> None:
        """!
        Sets the subject and observers for each strategy.

        @param strategy_list: List of strategies to use.

        @return None
        """
        for strategy in strategy_list:
            # Add MarketData Observers
            self.mkt_data_observers[strategy] = StrategyMarketDataObserver(
                self.data_queue[strategy])
            self.mkt_data_subjects.attach(self.mkt_data_observers[strategy])

            # Add Order Observers
            self.order_observers[strategy] = StrategyOrderDataObserver(self.data_queue[strategy])
            self.order_subjects.attach(self.order_observers[strategy])

            # Add Real Time Bar Observers
            self.rtb_observers[strategy] = StrategyRealTimeBarObserver(self.data_queue[strategy])
            self.rtb_subjects.attach(self.rtb_observers[strategy])
