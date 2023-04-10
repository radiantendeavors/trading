"""!@package pytrader.libs.applications.trader

The main user interface for the trading program.

@author Geoff S. Derber
@version HEAD
@date 2022
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

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
#from pytrader.libs.applications import broker
from pytrader.libs.applications import broker
from pytrader.libs.applications import strategy

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

    def __init__(self):
        self.cmd_queue = multiprocessing.Queue()
        self.data_queue = multiprocessing.Queue()

    def run_processes(self, processed_args):
        """!
        Runs the various subprocesses.

        @param processed_args: A list of arguments.

        @return None
        """
        logger.debug10("Begin Function")
        address = processed_args[0]
        strategy_list = processed_args[1]

        try:
            broker_client = broker.BrokerProcess(self.cmd_queue,
                                                 self.data_queue, address)
            broker_process = multiprocessing.Process(target=broker_client.run)
            broker_process.start()

            strat = strategy.StrategyProcess(self.cmd_queue, self.data_queue)
            strategy_process = multiprocessing.Process(target=strat.run,
                                                       args=(strategy_list, ))
            strategy_process.start()
        except KeyboardInterrupt as msg:
            logger.critical("Keyboard Interrupt, Closing Application: %s", msg)
        finally:
            strategy_process.join()
            broker_process.join()

        logger.debug10("End Function")


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
