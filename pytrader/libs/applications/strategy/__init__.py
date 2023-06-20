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
import threading

# 3rd Party Libraries

# Application Libraries
# Standard Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import utilities

# Conditional Libraries

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

    def __init__(self, cmd_queue, data_queue, next_order_id):
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.next_order_id = next_order_id

    def run(self, strategy_list):
        """!
        Runs the various strategies.
        """
        for index, strategy_path in enumerate(strategy_list):
            order_id = self.next_order_id + (index * 1000)
            logger.debug("Order Id for Strategy %s: %s", strategy_path, order_id)
            module_name = IMPORT_PATH + strategy_path
            module = importlib.import_module(module_name, __name__)
            strategy = module.Strategy(self.cmd_queue, self.data_queue, order_id)
            strategy_thread = threading.Thread(target=strategy.run)

            strategy_thread.start()
