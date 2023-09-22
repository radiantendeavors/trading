"""!@package pytrader.libs.applications.broker

Manages the broker processes

@author G S Derber
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

@file pytrader/libs/applications/broker/__init__.py
"""
# System Libraries
import multiprocessing
import threading
from multiprocessing import Process, Queue
from typing import Optional

# Application Libraries
from pytrader import git_branch
from pytrader.libs.clients.broker import BrokerClient
from pytrader.libs.system import logging
from pytrader.libs.utilities.exceptions import BrokerNotAvailable

# 3rd Party Libraries

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
class BrokerProcessManager():
    """!
    The Manages the Broker Processes
    """

    address = {}
    broker_clients = {}
    broker_configs = {}
    broker_processes = {}
    broker_cmd_queues = {}
    strategies = None
    client_id = None

    def __init__(self, brokers: list, cmd_queue: Queue, data_queue: dict) -> None:
        """!
        Creates an instance of the BrokerProcess.

        @return None
        """
        self.broker_list = brokers
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue

    def configure_brokers(self,
                          address: str,
                          client_id: Optional[int] = 0,
                          strategies: Optional[list] = None) -> None:
        """!
        Configures the various broker options

        @return None
        """
        # This function is written to allow multiple brokers be connected to simultaniously.  For
        # example, twsapi, and ibkrweb.  In addition, twsapi, can connect to multiple instances of
        # TraderWorkstation, or IBGateway.  So for each broker in the list, it gets a dictionary of
        # the possible connection settings for each broker, and appends it to the previously
        # gathered dictionaries of brokers.
        # Once all potential brokers are identified, create an instance of each broker client.
        if strategies:
            self.strategies = strategies

        self.client_id = client_id

        logger.debug("Strategies: %s", self.strategies)

        if "backtester" in self.broker_list:
            self._configure_backtester()
        else:
            for broker in self.broker_list:
                self._configure_brokers(broker, address)

        # for broker in list(self.brokers):
        #     logger.debug("Broker: %s", broker)
        #     self.broker_clients[broker] = BrokerClient(self.brokers[broker],
        #                                                self.broker_cmd_queues[broker],
        #                                                self.data_queue)

        #     self.broker_clients[broker].set_broker_observers(broker)

        #     try:
        #         self.broker_clients[broker].connect(self.address[broker])
        #     except BrokerNotAvailable as msg:
        #         logger.debug("Broker Not Available: %s", msg)
        #         self.broker_clients.pop(broker, None)
        #         continue

    def run(self) -> None:
        """!
        Run the broker process as long as the broker is connected.

        @return None
        """
        self._start_processes()

        broker_connection = True
        while broker_connection:
            cmd = self.cmd_queue.get()
            logger.debug("Command: %s", cmd)

            sender = list(cmd)[0]
            logger.debug("Sender: %s", sender)

            if cmd == "Quit":
                broker_connection = False
            else:
                logger.debug(self.broker_cmd_queues)
                sender = "tws_demo_" + sender
                self.broker_cmd_queues[sender].put(cmd)

    # def set_downloader(self) -> None:
    #     """!
    #     Configures the downloader observers.

    #     @return None
    #     """
    #     for broker in list(self.brokers):
    #         if broker in list(self.broker_clients):
    #             self.broker_clients[broker].set_downloader()

    # def set_main(self) -> None:
    #     """!
    #     Configures the main process observers.

    #     @return None
    #     """
    #     for broker in list(self.brokers):
    #         if broker in list(self.broker_clients):
    #             self.broker_clients[broker].set_main()

    # def set_strategies(self, strategy_list: list) -> None:
    #     """!
    #     Set's the strategies observers for message passing.

    #     @param strategy_list: A list of strategies

    #     @return None
    #     """
    #     self.strategies = strategy_list

    #     for broker in list(self.brokers):
    #         if broker in list(self.broker_clients):
    #             self.broker_clients[broker].set_strategies(strategy_list)

    def stop(self) -> None:
        """!
        Stops the brokerclient thread.

        @return None
        """
        for broker_id in list(self.broker_clients):
            logger.debug("Broker Id: %s", broker_id)
            logger.debug("Broker Processes: %s", self.broker_processes)

            # FIXME: The program doesn't always have broker_id in self.broker_processes.
            if broker_id in self.broker_processes:
                self.broker_processes[broker_id].join()

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _configure_backtester(self) -> None:
        logger.debug("Running Backtesting Broker")

    def _configure_brokers(self, broker: str, address: str) -> None:
        brokers = {}

        if git_branch == "main":
            brokers["twsapi"] = ["tws_real"]
        else:
            brokers["twsapi"] = ["tws_demo"]

        for broker_id in brokers[broker]:
            if broker == "twsapi":
                self._configure_twsapi_brokers(broker_id, address)

    def _configure_twsapi_brokers(self, broker_id: str, address: str) -> None:
        client_roles = ["order", "downloader"]
        if self.strategies:
            client_roles.insert(0, "strategy")

        for role in client_roles:
            client_id = broker_id + "_" + role
            self.broker_cmd_queues[client_id] = Queue()
            self.broker_clients[client_id] = BrokerClient(broker_id,
                                                          self.broker_cmd_queues[client_id],
                                                          self.data_queue, self.client_id)
            self.broker_clients[client_id].set_address(address)
            self.broker_clients[client_id].set_role(role)
            if role == "strategy":
                self.broker_clients[client_id].set_strategies(self.strategies)

            self.client_id += 1

    def _start_processes(self) -> None:
        """!
        Starts the broker client processes.

        @return None
        """
        logger.debug("Process Name: %s  Thread Name: %s",
                     multiprocessing.current_process().name,
                     threading.current_thread().name)

        for broker_id, brokerclient in self.broker_clients.items():
            logger.debug("Starting Brokerclient %s: %s", broker_id, brokerclient)
            self.broker_processes[broker_id] = Process(target=brokerclient.run, args=())
            self.broker_processes[broker_id].start()

        logger.debug("Broker Processes: %s", self.broker_processes)
