"""!@package pytrader.libs.applications.strategy

Provides the application process manager

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
# Standard Libraries
import importlib
import multiprocessing
from multiprocessing import Queue

# Application Libraries
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)

## The python formatted location of the strategies
IMPORT_PATH = "pytrader.strategies."


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class StrategyProcess():
    """!
    This prosess manages the various strategies that are running.
    """

    strategy_process = {}

    def __init__(self, cmd_queue: Queue, data_queue: dict, next_order_id: int,
                 fed_event: str) -> None:
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.next_order_id = next_order_id
        self.fed_event = fed_event

    def run(self, strategy_list: list) -> None:
        """!
        Runs the various strategies.

        @param strategy_list: List of strategies that will be run.

        @return None
        """
        for index, strategy_id in enumerate(strategy_list):
            order_id = self.next_order_id + (index * 1000)
            logger.debug("Order Id for Strategy %s: %s", strategy_id, order_id)
            module_name = IMPORT_PATH + strategy_id
            module = importlib.import_module(module_name, __name__)
            strategy = module.Strategy(self.cmd_queue, self.data_queue[strategy_id], order_id,
                                       strategy_id)
            self.strategy_process[strategy_id] = multiprocessing.Process(target=strategy.run,
                                                                         args=())
            self.strategy_process[strategy_id].start()

        logger.debug("Strategy Keys: %s", str(list(self.strategy_process)))

    def stop(self) -> None:
        """!
        Stops various strategy processes

        @param strategy_list: The list of strategies to stop.

        @return None
        """
        logger.debug10("Strategy Keys: %s", str(list(self.strategy_process)))
        try:
            for strategy_id in list(self.strategy_process):
                try:
                    self.strategy_process[strategy_id].join()
                except KeyError:
                    logger.debug9("Strategy '%s' already stopped", strategy_id)
        except AttributeError as msg:
            logger.error("AttributeError Stopping Strategy Processes: %s", msg)
