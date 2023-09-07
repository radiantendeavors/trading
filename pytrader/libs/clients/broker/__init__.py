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
import threading

from multiprocessing import Queue

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

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
class BrokerClient():
    """
    The BrokerClient.
    """
    strategies = None

    def __init__(self, brokerclient, cmd_queue: Queue, data_queue: dict):
        self.brokerclient = brokerclient
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue

    def connect(self, address: str, client_id: int):
        """!
        Connects to the broker client.
        """
        self.brokerclient.connect(address, client_id=client_id)
        self.brokerclient.start()

    def run(self) -> None:
        """!
        Runs the BrokerClient Process.

        @return None
        """
        broker_connection = True
        while broker_connection:
            cmd = self.cmd_queue.get()
            strategy_id = list(cmd)[0]

            self._process_commands(cmd[strategy_id], strategy_id)
            broker_connection = self.brokerclient.is_connected()

    def set_strategies(self, strategy_list: list) -> None:
        """!
        Sets the strategy observers for the brokerclient.

        @param strategy_list:

        @return None
        """
        self.strategies = strategy_list
        self.brokerclient.set_strategies(strategy_list)

    def _cancel_order(self, order_id: int) -> None:
        """!
        Send Cancel Order to brokerclient thread.
        """
        self.brokerclient.cancel_order(order_id)

    def _place_order(self, order_request: dict, strategy_id: str) -> None:
        """!
        Send place order to brokerclient thread.

        @param order_request:
        @param strategy_id:

        @return None
        """
        logger.debug9("Order Received: %s", order_request)
        self.brokerclient.create_order(order_request, strategy_id)

    def _process_commands(self, cmd: dict, strategy_id: str) -> None:
        """!
        Processes command received from other processes.

        @param cmd: The command received.
        @param strategy_id: The strategy that sent the command.

        @return None
        """
        logger.debug4("Processing Command: %s", cmd)
        if cmd.get("set"):
            self._set_cmd(cmd["set"], strategy_id)
        if cmd.get("req"):
            self._req_cmd(cmd["req"], strategy_id)
        if cmd.get("place_order"):
            self._place_order(cmd["place_order"], strategy_id)
        if cmd.get("cancel_order"):
            self._cancel_order(cmd["cancel_order"])

    def _req_cmd(self, subcommand: dict, strategy_id: str):
        logger.debug4("Request Command: %s", subcommand)
        if subcommand == "bar_history":
            self.brokerclient.request_bar_history()
        elif subcommand == "option_details":
            self.brokerclient.request_option_details(strategy_id)
        elif subcommand == "real_time_bars":
            self.brokerclient.request_real_time_bars(strategy_id)
        elif subcommand == "real_time_market_data":
            self.brokerclient.request_market_data(strategy_id)
        # elif subcommand == "tick_by_tick_data":
        #     self._request_tick_by_tick_data()
        elif subcommand == "global_cancel":
            self.brokerclient.request_global_cancel()
        else:
            logger.error("Command Not Implemented: %s", subcommand)

    # def _request_tick_by_tick_data(self):
    #     for key in list(self.contracts):
    #         self.ticks[key] = ticks.BrokerTicks(contract=self.contracts[key],
    #                                             brokerclient=self.brokerclient,
    #                                             data_queue=self.data_queue)
    #         self.ticks[key].request_ticks()
    #         self.tick_thread[key] = threading.Thread(
    #             target=self.ticks[key].run, daemon=True)
    #         self.tick_thread[key].start()

    def _set_cmd(self, subcommand: dict, strategy_id: str) -> None:
        """!
        Processes any subcommand from the 'set' command received from the strategy process.
        """
        logger.debug4("Subcommand received: %s", subcommand)
        if subcommand.get("tickers"):
            self.brokerclient.set_contracts(subcommand["tickers"], strategy_id)
            self.data_queue[strategy_id].put("Contracts Created")
        if subcommand.get("bar_sizes"):
            self.brokerclient.set_bar_sizes(subcommand["bar_sizes"], strategy_id)
            self.data_queue[strategy_id].put("Bar Sizes Set")
