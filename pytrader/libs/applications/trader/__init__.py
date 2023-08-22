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
from pytrader import BROKER_ID, CLIENT_ID
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

    def __init__(self) -> None:
        self.cmd_queue = multiprocessing.Queue()
        self.data_queue = {}
        self.broker_process = None
        self.strategy_process = None

    def run_processes(self,
                      address,
                      broker_id: str = BROKER_ID,
                      client_id: int = CLIENT_ID,
                      strategy_list: Optional[list] = None) -> None:
        """!
        Runs the various subprocesses.

        @param processed_args: A list of arguments.

        @return None
        """
        try:
            self._run_broker_process(address, broker_id, client_id, strategy_list)
            # This ensures we have the next order ID before doing anything else.
            next_order_id = 0
            while next_order_id == 0:
                message = self.data_queue["Main"].get()
                if message.get("next_order_id"):
                    next_order_id = message["next_order_id"]

            if strategy_list is not None and len(strategy_list) > 0:
                self._run_strategy_process(strategy_list, next_order_id)
        except BrokerNotAvailable as msg:
            logger.critical("Broker Not Available. %s", msg)

        except KeyboardInterrupt as msg:
            logger.critical("Keyboard Interrupt, Closing Application: %s", msg)
        finally:
            if len(strategy_list) > 0:
                self.strategy_process.join()

            self.cmd_queue.put("Quit")
            self.broker_process.join()

    def _run_broker_process(self,
                            address: str,
                            broker_id: str,
                            client_id: int,
                            strategy_list: Optional[list] = None) -> None:
        self.data_queue["Main"] = multiprocessing.Queue()

        if strategy_list is not None and len(strategy_list) > 0:
            for strategy_id in strategy_list:
                strategy_data_queue = multiprocessing.Queue()
                self.data_queue[strategy_id] = strategy_data_queue

        broker_client = broker.BrokerProcess(self.cmd_queue, self.data_queue, address, broker_id,
                                             client_id)
        if strategy_list is not None and len(strategy_list) > 0:
            broker_client.set_strategies(strategy_list)

        self.broker_process = multiprocessing.Process(target=broker_client.run)
        self.broker_process.start()

    def _run_strategy_process(self, strategy_list: list, next_order_id: int) -> None:
        strat = strategy.StrategyProcess(self.cmd_queue, self.data_queue, next_order_id)
        self.strategy_process = multiprocessing.Process(target=strat.run, args=(strategy_list, ))
        self.strategy_process.start()


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
