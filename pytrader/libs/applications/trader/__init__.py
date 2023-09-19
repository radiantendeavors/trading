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
class ProcessManager():
    """!
    This class is responsible for managing the various processes that are running.
    """
    cmd_queue = multiprocessing.Queue()
    reply_queue = {}
    brokers = None
    downloader = None
    strategies = None
    broker_process = None
    strategy_process = None
    downloader_process = None

    def __init__(self, args: argparse.Namespace) -> None:
        """!
        Initializes the Process Manager Class

        @param args: Command Line Arguments

        @return None
        """
        logger.debug9("Args: %s", args)
        self.broker_list = args.broker
        self.client_id = args.client_id
        self.strategy_list = args.strategies
        self.tickers = args.tickers
        self.enable_options = args.enable_options
        self.asset_classes = args.asset_classes
        self.currencies = args.currencies
        self.regions = args.regions
        self.export = args.export

        if len(self.strategy_list) > 0:
            for strategy_id in self.strategy_list:
                strategy_data_queue = multiprocessing.Queue()
                self.reply_queue[strategy_id] = strategy_data_queue

        self.reply_queue["downloader"] = multiprocessing.Queue()
        self.reply_queue["main"] = multiprocessing.Queue()

    def config_brokers(self) -> None:
        """!
        Configures the Brokers

        @return None
        """
        self.brokers = broker.BrokerProcessManager(self.broker_list, self.client_id, self.cmd_queue,
                                                   self.reply_queue)
        self.brokers.configure_brokers()

        if self.strategy_list is not None:
            self.brokers.set_strategies(self.strategy_list)

        self.brokers.set_downloader()
        self.brokers.set_main()

        try:
            self._run_broker_process()
        except KeyboardInterrupt as msg:
            logger.critical("Keyboard Interupt! %s", msg)

    def run(self) -> None:
        """!
        Runs the various subprocesses.

        @return None
        """
        try:
            # This ensures we have the next order ID before doing anything else.
            next_order_id = 0
            while next_order_id == 0:
                message = self.reply_queue["main"].get()
                if message.get("next_order_id"):
                    next_order_id = message["next_order_id"]

            logger.debug("Next Order Id: %s", next_order_id)

            self._run_downloader_process()

            if self.strategy_list is not None:
                logger.debug("Starting Straties: %s", self.strategy_list)
                self._run_strategy_process(self.strategy_list, next_order_id)

            # FIXME: Determine what will actually end this process.
            while True:
                pass

        except BrokerNotAvailable as msg:
            logger.critical("Broker Not Available. %s", msg)

        except KeyboardInterrupt as msg:
            logger.critical("Keyboard Interrupt, Closing Application: %s", msg)
        finally:
            if self.strategy_list is not None:
                self._stop_strategy_process(self.strategy_list)

            self._stop_broker_process()

    def _run_broker_process(self) -> None:
        self.broker_process = multiprocessing.Process(target=self.brokers.run, args=())
        self.broker_process.start()

    def _run_downloader_process(self) -> None:
        self.downloader = downloader.DownloadProcess(self.cmd_queue, self.reply_queue["downloader"],
                                                     self.tickers, self.enable_options,
                                                     self.asset_classes, self.currencies,
                                                     self.regions, self.export)
        self.downloader_process = multiprocessing.Process(target=self.downloader.run, args=())
        self.downloader_process.start()

    def _run_strategy_process(self, strategy_list: list, next_order_id: int) -> None:
        self.strategies = strategy.StrategyProcess(self.cmd_queue, self.reply_queue, next_order_id)
        self.strategy_process = multiprocessing.Process(target=self.strategies.run,
                                                        args=(strategy_list, ))
        self.strategy_process.start()

    def _stop_broker_process(self):
        try:
            self.brokers.stop()
            self.broker_process.join()
        except AttributeError as msg:
            logger.error("AttributeError Stopping Broker Processes: %s", msg)

    def _stop_downloader_process(self) -> None:
        self.downloader_process.join()

    def _stop_strategy_process(self, strategy_list: list):
        try:
            # We add this check here because if the strategies aren't started above because we never
            # receive the next order id, then self.strategies will still be NoneType.
            if self.strategies is not None:
                self.strategies.stop(strategy_list)
                self.strategy_process.join()
        except AttributeError as msg:
            logger.error("AttributeError Stopping Strategy Processes: %s", msg)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
