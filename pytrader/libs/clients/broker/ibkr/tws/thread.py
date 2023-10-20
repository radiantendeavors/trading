"""!
@package pytrader.libs.clients.broker
Creates a basic interface for interacting with a broker

@file pytrader/libs/clients/broker/__init__.py

Creates a basic interface for interacting with a broker

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

"""
# System Libraries
import multiprocessing
import threading
from queue import Queue
from typing import Optional

# Application Libraries
from pytrader.libs.clients.broker.ibkr.tws.reader import TwsReader
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
class TwsThreadMngr(TwsReader):
    """!
    Manages the thread for the TWS API Client.
    """

    def __init__(self):
        self.api_thread = threading.Thread(target=self.run, daemon=True)
        super().__init__()

    def start(self, role: str, data_queue: dict, queue: Queue, strategies: Optional[list]) -> None:
        """!
        Starts the api thread.

        @param thread_queue: The thread message passing queue.

        @return None
        """
        self.data_queue = data_queue
        logger.debug("Process Name: %s", multiprocessing.current_process().name)
        logger.debug("Thread Name: %s", threading.current_thread().name)
        self.api_thread.start()
        logger.debug("Process Name: %s", multiprocessing.current_process().name)
        logger.debug("Thread Name: %s", threading.current_thread().name)

        logger.debug(self.data_queue)

        logger.debug("Role: %s", role)
        if role == "strategy":
            self.config_strategy_observers(strategies)
        if role == "downloader":
            self.config_downloader_observers()

        self.config_broker_observers(role, queue)
        self.config_main_observers()

        logger.debug("Starting Thread")

    def stop(self) -> None:
        """!
        Stops the api thread.

        @return None.
        """
        try:
            self.api_thread.join()
        except AttributeError as msg:
            logger.error("AttributeError Stopping TwsApiClient Thread: %s", msg)
