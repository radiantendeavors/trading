"""!@package pytrader.libs.applications.pytrader

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
import queue

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients import broker
from pytrader.libs import utilities

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base logger
logger = logging.getLogger(__name__)

## Client ID Used for the Interactive Brokers API
client_id = 1001

## The python formatted location of the strategies
import_path = "pytrader.strategies."


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
        ## Used for tracking the broker process.
        self.broker_process = None

        ## Used far tracking the strategy processes.
        self.strategy_processes = []

    def brokerclient_process(self, brokerclient, process_queue):
        # brokerclient.connect(address, port, client_id)
        brokerclient.start_thread(process_queue)

        next_order_id = brokerclient.get_next_order_id()
        logger.debug("Received next order id: %s", next_order_id)
        return None

    def start_brokerclient_process(self, brokerclient, process_queue):
        # self.broker_process = multiprocessing.Process(
        #     target=self.brokerclient_process,
        #     args=(brokerclient, process_queue))
        # self.broker_process.start()
        self.brokerclient_process(brokerclient, process_queue)
        return None

    def stop_brokerclient_process(self, brokerclient):
        # self.broker_process.join()
        # brokerclient.stop_thread()
        brokerclient.disconnect()

    def start_strategy_process(self, strategy, brokerclient, process_queue,
                               securities_list, bar_sizes):
        logger.debug10("Begin Function")
        # strategy_process = multiprocessing.Process(
        #     target=strategy,
        #     args=(brokerclient, process_queue, securities_list, bar_sizes))
        # strategy_process.start()
        strategy(brokerclient, process_queue, securities_list, bar_sizes)
        logger.debug10("End Function")
        #return strategy_process
        return None

    def run_processes(self, processed_args):
        address = processed_args[0]
        port = processed_args[1]
        strategy_list = processed_args[2]
        bar_sizes = processed_args[3]
        securities = processed_args[4]

        process_queue = multiprocessing.Queue()
        brokerclient = broker.brokerclient("ibkr")
        brokerclient.connect(address, port, client_id)

        logger.debug("Starting Processes")

        self.start_brokerclient_process(brokerclient, process_queue)

        self.strategy_processes = {}
        for i in strategy_list:
            strategy = utilities.get_plugin_function(program=i,
                                                     cmd='run',
                                                     import_path=import_path)
            self.start_strategy_process(strategy, brokerclient, process_queue,
                                        securities, bar_sizes)

        logger.debug("Processes Started")

        logger.debug("Stopping Processes")
        self.stop_brokerclient_process(brokerclient)

        # for i in self.strategy_processes:
        #     i.join()

        logger.debug("Processes Stopped")

        logger.debug10("End Function")
        return None


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
