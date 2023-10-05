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
from multiprocessing import Queue
from typing import Optional

from pytrader.libs.clients.broker.ibkr.tws import (IbgDemoAccountClient,
                                                   IbgRealAccountClient,
                                                   TwsDemoAccountClient,
                                                   TwsRealAccountClient)
# Application Libraries
from pytrader.libs.system import logging

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
class BrokerClient():
    """
    The BrokerClient.
    """
    address = None
    strategies = None
    role = None

    def __init__(self,
                 brokerclient: str,
                 cmd_queue: Queue,
                 data_queue: dict,
                 client_id: Optional[int] = 0) -> None:
        """!
        Initializes an instance of the BrokerClient Class.

        @param brokerclient:
        @param cmd_queue:
        @param data_queue:
        @param client_id:

        @return None
        """
        self.brokerclient = self._select_broker_client(brokerclient, data_queue)
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.client_id = client_id

    def run(self) -> None:
        """!
        Runs the BrokerClient Process.

        @return None
        """
        self.brokerclient.connect(self.address, self.client_id)
        self.brokerclient.start(self.role, self.strategies)

        broker_connection = True
        while broker_connection:
            cmd = self.cmd_queue.get()
            commander_id = list(cmd)[0]

            self._process_commands(cmd[commander_id], commander_id)
            broker_connection = self.brokerclient.is_connected()

    def set_strategies(self, strategy_list: list) -> None:
        """!
        Sets the strategy observers for the brokerclient.

        @param strategy_list:

        @return None
        """
        self.strategies = strategy_list

    def set_address(self, address: str) -> None:
        """!
        Sets the address for the brokerclient.

        @param address:

        @return None
        """
        self.address = address

    def set_role(self, role: str) -> None:
        """!
        Sets the role for the brokerclient.

        @param role:

        @return None
        """
        self.role = role

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
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
        if cmd.get("req"):
            self._req_cmd(cmd["req"], strategy_id)
        if cmd.get("place_order"):
            self._place_order(cmd["place_order"], strategy_id)
        if cmd.get("cancel_order"):
            self._cancel_order(cmd["cancel_order"])

    def _req_cmd(self, subcommand: dict, strategy_id: str):
        logger.debug4("Request Command: %s", subcommand)

        command = list(subcommand)[0]

        match command:
            case "bar_history":
                self.brokerclient.request_bar_history()
            case "contract_details":
                self.brokerclient.request_contract_details(subcommand[command])
            case "history_begin_date":
                self.brokerclient.request_history_begin_date(subcommand[command])
            case "option_details":
                self.brokerclient.request_option_details(subcommand[command])
            case "real_time_bars":
                self.brokerclient.request_real_time_bars(strategy_id)
            case "real_time_market_data":
                self.brokerclient.request_market_data(strategy_id)
            case "tick_by_tick_data":
                logger.warning("Tick By Tick Data Not Implemented")
                # self._request_tick_by_tick_data()
            case "global_cancel":
                self.brokerclient.request_global_cancel()
            case _:
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

    def _select_broker_client(self, brokerclient: str, data_queue):
        client_classes = {
            "tws_real": TwsRealAccountClient,
            "tws_demo": TwsDemoAccountClient,
            "ibg_real": IbgRealAccountClient,
            "ibg_demo": IbgDemoAccountClient
        }

        return client_classes[brokerclient](data_queue)
