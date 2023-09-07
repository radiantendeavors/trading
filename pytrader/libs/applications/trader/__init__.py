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
import multiprocessing

from typing import Optional

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader import CLIENT_ID
from pytrader.libs.applications import broker
from pytrader.libs.applications import strategy
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
    data_queue = {"main": multiprocessing.Queue()}
    brokers = None
    strategies = None
    broker_process = None
    strategy_process = None

    def __init__(self,
                 broker_list: list,
                 strategy_list: Optional[list] = None,
                 client_id: Optional[int] = CLIENT_ID):
        self.broker_list = broker_list
        self.client_id = client_id
        self.strategy_list = None

        if strategy_list is not None and len(strategy_list) > 0:
            self.strategy_list = strategy_list
            for strategy_id in strategy_list:
                strategy_data_queue = multiprocessing.Queue()
                self.data_queue[strategy_id] = strategy_data_queue

    def config_brokers(self) -> None:
        """!
        Configures the Brokers

        @return None
        """
        self.brokers = broker.BrokerProcessManager(self.broker_list, self.client_id, self.cmd_queue,
                                                   self.data_queue)
        self.brokers.configure_brokers()

        if self.strategy_list is not None:
            self.brokers.set_strategies(self.strategy_list)

    def run(self) -> None:
        """!
        Runs the various subprocesses.

        @param address: The ip address or url of the broker
        @param broker_id: The Broker identity to connect to.
        @param client_id: The client id sent to the broker.
        @param strategy_list: Optional list of strategies to run.

        @return None
        """
        try:
            self._run_broker_process()
            # This ensures we have the next order ID before doing anything else.
            next_order_id = 0
            while next_order_id == 0:
                message = self.data_queue["main"].get()
                if message.get("next_order_id"):
                    next_order_id = message["next_order_id"]

            if self.strategy_list is not None:
                logger.debug("Starting Straties: %s", self.strategy_list)
                self._run_strategy_process(self.strategy_list, next_order_id)

            # We need to essentially stop here as long as the broker process manager is alive.
            while self.broker_process.is_alive():
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

    def _stop_broker_process(self):
        try:
            self.brokers.stop()
            self.broker_process.join()
        except AttributeError as msg:
            logger.error("AttributeError Stopping Broker Processes: %s", msg)

    def _run_strategy_process(self, strategy_list: list, next_order_id: int) -> None:
        self.strategies = strategy.StrategyProcess(self.cmd_queue, self.data_queue, next_order_id)
        self.strategy_process = multiprocessing.Process(target=self.strategies.run,
                                                        args=(strategy_list, ))
        self.strategy_process.start()

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
