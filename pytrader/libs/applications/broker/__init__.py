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
from multiprocessing import Process, Queue

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.broker import BrokerClient
from pytrader.libs.utilities.config.broker import BrokerConfig

# Conditional Libraries

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
    brokers = {}
    broker_configs = {}
    broker_processes = {}
    broker_clients = {}
    broker_cmd_queues = {}

    def __init__(self, broker_list: list, client_id: int, cmd_queue: Queue,
                 data_queue: dict) -> None:
        """!
        Creates an instance of the BrokerProcess.

        @return None
        """
        self.broker_list = broker_list
        self.client_id = client_id
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.strategies = None

    def configure_brokers(self) -> None:
        """!
        Configures the various broker options

        @return None
        """
        # This function is written to allow multiple brokers be connected to simultaniously.  For
        # example, twsapi, and ibkrweb.  In addition, twsapi, can connect to multiple instances of
        # TraderWorkstation, or IBGateway.  So for each broker in the list, it gets a dictionary of
        # the possible connection settings for each broker, and appends it to the previously
        # gathered dictionaries of brokers.
        brokers = {}
        addresses = {}
        for broker in self.broker_list:
            self.broker_configs[broker] = BrokerConfig(broker)
            brokers.update(self.broker_configs[broker].identify_clients())
            addresses[broker] = self.broker_configs[broker].get_client_address()

        # Once all potential brokers are identified, create an instance of each broker client.
        for broker in list(brokers):
            self.broker_cmd_queues[broker] = Queue()
            self.brokers[broker] = brokers[broker](self.data_queue)
            # FIXME: This is so fucked up.
            self.address[broker] = addresses[self.broker_list[0]]

        for broker in list(self.brokers):
            self.broker_clients[broker] = BrokerClient(self.brokers[broker],
                                                       self.broker_cmd_queues[broker],
                                                       self.data_queue)
            self.broker_clients[broker].connect(self.address[broker], self.client_id)

    def run(self) -> None:
        """!
        Run the broker process as long as the broker is connected.

        @return None
        """
        self._start_processes()

        try:
            broker_connection = True
            while broker_connection:
                cmd = self.cmd_queue.get()
                logger.debug4("Command: %s", cmd)

                if cmd == "Quit":
                    broker_connection = False
                else:
                    # TODO: Determine how to distribute the cmd requests among the different broker
                    # clients.
                    #
                    # For order placement, this will be dependent upon which account to send the
                    # order to as long as there is only one client connected to that account.
                    #
                    # For streaming market data, it makes sense to consolidate strategies that use
                    # the same ticker symbols together, so we aren't requesting duplicate data.
                    #
                    # At the same time, some duplication may help with failover.
                    #
                    # Because of the limits on the number of tickers that can be requested for
                    # streaming data, it also makes sense to distribute the different tickers among
                    # the different clients.
                    #
                    # For historical data, it may make sense to load balance among available
                    # clients.
                    #
                    # To make it more complicated, if you have two clients for TwsApi connected to
                    # the real account, that has the same limitations as a single client.  Whereas,
                    # one client connected to the real account, and one client connected to a demo
                    # account, may have separate limitations.  May be because it depends on how the
                    # user has set up their paper trading account data permissions.
                    #
                    # In addition, each client may have different limits on the number of data
                    # requests it can make.  So we'll need to track how many outstanding requests
                    # each client has.
                    #
                    # Figuring out how to do this properly is a fucking mess.
                    #
                    # For now, we send all data requests to the 1st client.
                    broker = list(self.broker_clients)[0]
                    self.broker_cmd_queues[broker].put(cmd)

        except KeyboardInterrupt:
            logger.critical("Received Keyboard Interrupt! Shutting down the Broker Clients.")

    def set_strategies(self, strategy_list: list) -> None:
        """!
        Set's the strategies observers for message passing.

        @param strategy_list: A list of strategies

        @return None
        """
        self.strategies = strategy_list

        for broker in list(self.brokers):
            self.broker_clients[broker].set_strategies(strategy_list)

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
    def _start_processes(self) -> None:
        """!
        Starts the broker client processes.

        @return None
        """
        logger.debug("Client Id: %s", self.client_id)
        logger.debug("Broker Clients: %s", self.broker_clients)

        for broker_id, brokerclient in self.broker_clients.items():
            logger.debug("Brokerclient: %s", brokerclient)
            self.broker_processes[broker_id] = Process(target=brokerclient.run, args=())
            self.broker_processes[broker_id].start()

        logger.debug("Broker Processes: %s", self.broker_processes)
