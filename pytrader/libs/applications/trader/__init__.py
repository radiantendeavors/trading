"""!@package pytrader.libs.applications.trader

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

@file pytrader/libs/applications/trader/__init__.py
"""

# System libraries
import argparse
import multiprocessing

# Application Libraries
from pytrader.libs.applications import broker, downloader, strategy
from pytrader.libs.applications.database import DatabaseManager
from pytrader.libs.system import logging
from pytrader.libs.utilities.exceptions import BrokerNotAvailable

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class SingletonMeta(type):
    """!
    This class is to ensure we only ever have 1 instance of the process manager.
    """

    __instances = {}

    def __call__(cls, *args, **kwargs):
        """!

        @param *args:
        @param *kwargs:
        """
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        return cls.__instances[cls]


# pylint: disable=R0902
class ProcessManager(metaclass=SingletonMeta):
    """!
    This class is responsible for managing the various processes that are running.
    """
    cmd_queue = multiprocessing.Queue()
    reply_queue = {}
    broker_mngr = None
    downloader_mngr = None
    strategy_mngr = None
    strategies = None
    broker_process = None
    strategy_process = None
    downloader_process = None
    next_order_id = 0

    def __init__(self, args: argparse.Namespace) -> None:
        """!
        Initializes the Process Manager Class

        @param args: Command Line Arguments

        @return None
        """
        logger.debug9("Args: %s", args)
        self.brokers = args.brokers
        self.address = args.address
        self.client_id = args.client_id
        self.strategies = args.strategies
        self.tickers = args.tickers
        self.asset_classes = args.asset_classes
        self.currencies = args.currencies
        self.regions = args.regions
        self.fed_event = args.fed
        self.enable_downloader = args.enable_downloader

        if len(self.strategies) > 0:
            for strategy_id in self.strategies:
                strategy_data_queue = multiprocessing.Queue()
                self.reply_queue[strategy_id] = strategy_data_queue

        self.reply_queue["downloader"] = multiprocessing.Queue()
        self.reply_queue["main"] = multiprocessing.Queue()

    def start(self, enable_broker: bool) -> None:
        """!
        Starts the various Subprocesses

        @param enable_broker: Weither we wish to enable the broker processes or not.

        @return None
        """
        self._run_database_mngr()

        if enable_broker:
            self._configure_broker()

        self._run_downloader_process()

        # If we disabled the broker, there is no point in running the strategies.
        if self.strategies is not None and enable_broker:
            logger.debug("Starting Straties: %s", self.strategies)
            self._run_strategy_process(self.strategies, self.next_order_id)

        self.run()

    def stop(self) -> None:
        """!
        Stops all processes.

        @return None
        """
        if self.strategies is not None:
            self._stop_strategy_process()

        self._stop_downloader_process()
        self._stop_broker_process()

    def run(self) -> None:
        """!
        Runs the various subprocesses.

        @return None
        """
        # FIXME: Determine what will actually end this process.
        while True:
            pass

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _configure_broker(self) -> None:
        self.broker_mngr = broker.BrokerProcessManager(self.brokers, self.cmd_queue,
                                                       self.reply_queue)
        self.broker_mngr.configure_brokers(self.address, self.client_id, self.strategies)
        self._run_broker_process()

        # This ensures we have the next order ID before doing anything else.
        while self.next_order_id == 0:
            message = self.reply_queue["main"].get()
            if message.get("next_order_id"):
                self.next_order_id = message["next_order_id"]

        logger.debug("Next Order Id: %s", self.next_order_id)

    def _run_broker_process(self) -> None:
        self.broker_process = multiprocessing.Process(target=self.broker_mngr.run, args=())
        self.broker_process.start()

    def _run_database_mngr(self) -> None:
        dbmgr = DatabaseManager()
        dbmgr.run()

    def _run_downloader_process(self) -> None:
        self.downloader_mngr = downloader.DownloadProcess(self.cmd_queue,
                                                          self.reply_queue["downloader"])
        if self.enable_downloader:
            self.downloader_mngr.enable_historical_downloader(self.asset_classes, self.regions,
                                                              self.currencies, self.tickers)
        self.downloader_process = multiprocessing.Process(target=self.downloader_mngr.run, args=())
        self.downloader_process.start()

    def _run_strategy_process(self, strategy_list: list, next_order_id: int) -> None:
        self.strategy_mngr = strategy.StrategyProcess(self.cmd_queue, self.reply_queue,
                                                      next_order_id, self.fed_event)
        self.strategy_process = multiprocessing.Process(target=self.strategy_mngr.run,
                                                        args=(strategy_list, ))
        self.strategy_process.start()

    def _stop_broker_process(self):
        try:
            self.broker_mngr.stop()
            self.broker_process.join()
        except AttributeError as msg:
            logger.error("AttributeError Stopping Broker Processes: %s", msg)

    def _stop_downloader_process(self) -> None:
        self.downloader_process.join()

    def _stop_strategy_process(self):
        try:
            # We add this check here because if the strategies aren't started above because we never
            # receive the next order id, then self.strategies will still be NoneType.
            if self.strategies is not None and len(self.strategies) > 0:
                self.strategy_mngr.stop()
                self.strategy_process.join()
        except AttributeError as msg:
            logger.error("AttributeError Stopping Strategy Processes: %s", msg)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
