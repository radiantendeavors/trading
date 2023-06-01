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
from pytrader.libs.applications import broker
from pytrader.libs.applications import downloader
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
        self.strategy_list = []
        self.broker_process = None
        self.strategy_process = None
        self.downloader_process = None

    def add_strategy(self, new_strategy: str):
        """!
        Add a single strategy to the list of managed strategies

        @param strategy: Strategy to add

        @return None
        """
        self.strategy_list.append(new_strategy)

    def add_strategy_list(self, strategies: list):
        """!
        Adds a list of strategies to the list of managed strategies.

        @param strategies: list of strategies to add.

        @return None
        """
        new_list = list(set(self.strategy_list + strategies))
        self.strategy_list = new_list

    def run(self, *args, **kwargs):
        """!
        Runs the various subprocesses.

        @param processed_args: A list of arguments.

        @return None
        """
        logger.debug("Begin Function")
        address = args[0]
        client_id = args[1]

        try:
            self._start_broker_process(address, client_id)

            # if len(self.strategy_list) > 0:
            #     self._start_strategy_process()
            # elif kwargs.get("downloader"):
            #     if kwargs.get("asset_classes"):
            #         asset_classes = kwargs["asset_classes"]

            #     if kwargs.get("securities_list"):
            #         securities_list = kwargs["securities_list"]
            #     else:
            #         securities_list = []

            #     self._start_downloader_process(asset_classes, securities_list)
        except KeyboardInterrupt as msg:
            logger.critical("Keyboard Interrupt, Closing Application: %s", msg)
        finally:
            if len(self.strategy_list) > 0:
                self._stop_strategy_process()
            if kwargs.get("downloader"):
                self._stop_downloader_process()
            self._stop_broker_process()

        logger.debug10("End Function")

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _start_broker_process(self, address, client_id):
        """!
        Starts the Broker Process.

        @param address: The broker address.
        @param client_id: The Broker Client Id.

        @return None
        """
        logger.debug("Starting Broker Process")
        if self.broker_process is None:
            broker_process_manager = broker.BrokerProcess(
                self.cmd_queue, self.data_queue)
            broker_process_manager.configure_client(address, client_id)
            self.broker_process = multiprocessing.Process(
                target=broker_process_manager.run)
            self.broker_process.start()

    def _start_downloader_process(self, asset_classes, securities_list: list):
        """!
        Starts the downloader process.
        """
        logger.debug("Starting Downloader Process")
        if self.downloader_process is None:
            downloader_ = downloader.DownloadProcess(self.cmd_queue,
                                                     self.data_queue)

            self.downloader_process = multiprocessing.Process(
                target=downloader_.run, args=(asset_classes, securities_list))
            self.downloader_process.start()

    def _start_strategy_process(self):
        """!
        Starts the stratagy manager process.
        """
        logger.debug("Starting Strategy Manager Process")
        if self.strategy_process is None:
            strat = strategy.StrategyProcess(self.cmd_queue, self.data_queue)
            self.strategy_process = multiprocessing.Process(
                target=strat.run, args=(self.strategy_list, ))
            self.strategy_process.start()

    def _stop_broker_process(self):
        """!
        Stops the broker process.
        """
        if self.broker_process is not None:
            self.broker_process.join()
            self.broker_process = None

    def _stop_downloader_process(self):
        """!
        Stops the downloader process.
        """
        if self.downloader_process is not None:
            self.downloader_process.join()
            self.downloader_process = None

    def _stop_strategy_process(self):
        """!
        Stops the strategy process.
        """
        if self.strategy_process is not None:
            self.strategy_process.join()
            self.strategy_process = None


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
