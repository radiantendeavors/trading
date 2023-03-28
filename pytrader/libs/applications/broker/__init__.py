"""!@package pytrader.libs.applications.broker

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

@file pytrader/libs/applications/broker/__init__.py
"""
# System Libraries
import queue
import socket
import threading

# 3rd Party Libraries
from ibapi import contract
from ibapi import order

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.applications.broker import bars
from pytrader.libs.applications.broker import marketdata
from pytrader.libs.applications.broker import ticks
from pytrader.libs.clients import broker
from pytrader.libs.utilities import ipc

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)

## List of potential ports TWS/IB Gateway could listen on.
ALLOWED_PORTS = [7496, 7497, 4001, 4002]


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BrokerProcess():
    """!
    The Process for interacting with the broker.

    """

    def __init__(self, address: str = "127.0.0.1"):
        """!
        Creates an instance of the BrokerProcess.
        """
        self.address = address
        self.available_ports = []
        self.brokerclient = broker.BrokerClient("ibkr")
        self.contracts = {}
        self.socket_server = ipc.IpcServer()
        self.client_id = 2003
        self.bars = {}
        self.ticks = {}
        self.market_data = {}
        self.rtb_thread = {}
        self.tick_thread = {}
        self.market_data_thread = {}
        self.broker_queue = queue.Queue()
        self.socket_recv_queue = queue.Queue()
        self.socket_send_queue = queue.Queue()

    def run(self):
        """!
        Run the broker process as long as the broker is connected.

        @param client_id: The ID number to use for the broker connection.
        """
        self._set_broker_ports()
        self._start_threads()

        logger.debug3("Socket Thread Started")

        broker_connection = True
        while broker_connection:
            logger.debug4("Loop while connected")
            cmd = self.socket_recv_queue.get()
            logger.debug2("Command: %s", cmd)
            logger.debug3("Command Data Type: %s", type(cmd))

            self._process_commands(cmd)
            broker_connection = self.brokerclient.is_connected()

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _check_if_ports_available(self, port):
        """!
        Checks if a given port is available

        @param port: The port to check

        @return bool: True if the port is available, False if it is not available.
        """
        logger.debug10("Begin Function")
        tws_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.debug10("End Function")
        return tws_socket.connect_ex((self.address, port)) == 0

    def _create_contracts(self, tickers):
        """!
        Takes a list of tickers, and creates contracts for them.

        @param tickers: The list of tickers

        @return None
        """
        logger.debug10("Begin Function")
        for item in tickers:
            if not self.contracts.get(item):
                logger.debug2("Creating contract for %s", item)
                contract_ = contract.Contract()
                contract_.symbol = item
                contract_.secType = "STK"
                contract_.exchange = "SMART"
                contract_.currency = "USD"
                self.contracts[item] = self._set_contract_details(contract_)

            self.bars[item] = {}
        logger.debug10("End Function")

    def _create_braket_order(self, order_request):
        ticker = order_request["ticker"]
        order_contract = self.contracts[ticker]
        ticker_index_id = list(self.contracts.keys()).index(ticker)
        order_id = self.brokerclient.next_order_id + ticker_index_id

        parent_order = order.Order()
        parent_order.orderId = order_id
        parent_order.action = order_request["action"]
        parent_order.orderType = "LMT"
        parent_order.totalQuantity = order_request["quantity"]
        parent_order.lmtPrice = order_request["price"]
        parent_order.transmit = False

        profit_order = order.Order()
        profit_order.orderId = parent_order.orderId + 1
        if order_request["action"] == "BUY":
            profit_order.action = "SELL"
        else:
            profit_order.action = "BUY"
        profit_order.orderType = "LMT"
        profit_order.totalQuantity = order_request["quantity"]
        profit_order.lmtPrice = order_request["profit_target"]
        profit_order.parentId = parent_order.orderId
        profit_order.transmit = False

        stop_order = order.Order()
        stop_order.orderId = parent_order.orderId + 2
        if order_request["action"] == "BUY":
            stop_order.action = "SELL"
        else:
            stop_order.action = "BUY"
        stop_order.orderType = "STP"
        stop_order.totalQuantity = order_request["quantity"]
        stop_order.auxPrice = order_request["stop_loss"]
        stop_order.parentId = parent_order.orderId
        stop_order.transmit = True

        self.brokerclient.place_order(order_contract, parent_order,
                                      parent_order.orderId)
        self.brokerclient.place_order(order_contract, profit_order,
                                      profit_order.orderId)
        self.brokerclient.place_order(order_contract, stop_order,
                                      stop_order.orderId)

    def _create_option_contracts(self):
        for key in self.contracts.keys():
            opt_details = self._request_option_details(self.contracts[key])

            expiry_set = set()
            strike_set = set()
            for key in opt_details:
                if key == "expirations":
                    expiry = expiry_set.union(opt_details[key])
                if key == "multiplier":
                    multiplier = opt_details[key]
                if key == "strikes":
                    strikes = strike_set.union(opt_details[key])

            expiry = list(expiry_set)
            strikes = list(strike_set)

            expiry.sort()
            strikes.sort()

    def _create_order(self, order_request):
        order_contract = self.contracts[order_request["ticker"]]

        parent_order = order.Order()
        parent_order.action = order_request["action"]
        parent_order.orderType = order_request["order_type"]
        parent_order.quantity = order_request["quantity"]

        if order_request.get("price"):
            parent_order.lmtPrice = order_request["price"]

        parent_order.transmit = True

        self.brokerclient.place_order(order_contract, parent_order)

    def _place_order(self, order_request):
        logger.debug("Order Received: %s", order_request)

        bracket_check = (order_request.get("profit_target")
                         and order_request.get("stop_loss"))

        logger.debug("Bracket Check: %s", bracket_check)
        if bracket_check:
            self._create_braket_order(order_request)
        else:
            self._create_order(order_request)

    def _process_commands(self, cmd):
        logger.debug("Processing Command: %s", cmd)
        if cmd.get("set"):
            self._set_cmd(cmd["set"])

        if cmd.get("req"):
            self._req_cmd(cmd["req"])

        if cmd.get("place_order"):
            self._place_order(cmd["place_order"])

    def _req_cmd(self, subcommand):
        if subcommand == "bar_history":
            self._request_bar_history()
        elif subcommand == "option_details":
            self._request_option_details()
        elif subcommand == "real_time_market_data":
            self._request_market_data()
        elif subcommand == "real_time_bars":
            self._request_real_time_bars()
        elif subcommand == "tick_by_tick_data":
            self._request_tick_by_tick_data()
        else:
            logger.error("Command Not Implemented: %s", subcommand)

    def _request_bar_history(self):
        for key in self.contracts.keys():
            for size in self.bars[key].keys():
                self.bars[key][size].retrieve_bar_history()

    def _request_option_details(self, contract_):
        req_id = self.brokerclient.req_sec_def_opt_params(contract_)
        return self.brokerclient.get_data(req_id)

    def _request_market_data(self):
        for key in self.contracts.keys():
            self.market_data[key] = marketdata.BrokerMarketData(
                contract=self.contracts[key],
                brokerclient=self.brokerclient,
                socket_queue=self.socket_send_queue)
            self.market_data[key].request_market_data()
            self.market_data_thread[key] = threading.Thread(
                target=self.market_data[key].run, daemon=True)
            self.market_data_thread[key].start()

    def _request_real_time_bars(self):
        for key in self.contracts.keys():
            self.bars[key]["rtb"] = bars.BrokerBars(
                contract=self.contracts[key],
                bar_size="rtb",
                brokerclient=self.brokerclient,
                socket_queue=self.socket_send_queue)

            self.bars[key]["rtb"].request_real_time_bars()

            self.rtb_thread[key] = threading.Thread(
                target=self.bars[key]["rtb"].run, daemon=True)
            self.rtb_thread[key].start()

    def _request_tick_by_tick_data(self):
        for key in self.contracts.keys():
            self.ticks[key] = ticks.BrokerTicks(
                contract=self.contracts[key],
                brokerclient=self.brokerclient,
                socket_queue=self.socket_send_queue)
            self.ticks[key].request_ticks()
            self.tick_thread[key] = threading.Thread(
                target=self.ticks[key].run, daemon=True)
            self.tick_thread[key].start()

    def _set_contract_details(self, contract):
        req_id = self.brokerclient.req_contract_details(contract)
        contract_details = self.brokerclient.get_data(req_id)
        return contract_details.contract

    def _set_broker_ports(self):
        """!
        Creates a list of available ports to connect to the broker.
        """
        logger.debug10("Begin Function")
        # for port in ALLOWED_PORTS:
        #     if self._check_if_ports_available(int(port)):
        #         self.available_ports.append(int(port))
        self.available_ports.append(int(7497))
        logger.debug2("Available ports: %s", self.available_ports)
        logger.debug10("End Function")

    def _set_cmd(self, subcommand):
        """!
        Processes any subcommand from the 'set' command received from the strategy process.
        """
        logger.debug10("Begin Function")
        if subcommand.get("tickers"):
            self._create_contracts(subcommand["tickers"])
            self.socket_send_queue.put("Contracts Created")
        if subcommand.get("bar_sizes"):
            self._set_bar_sizes(subcommand["bar_sizes"])
            self.socket_send_queue.put("Bar Sizes Set")
        logger.debug10("End Function")

    def _set_bar_sizes(self, bar_sizes):
        for key in self.contracts.keys():
            self.bars[key] = {}
            for item in bar_sizes:
                self.bars[key][item] = bars.BrokerBars(
                    contract=self.contracts[key],
                    bar_size=item,
                    brokerclient=self.brokerclient,
                    socket_queue=self.socket_send_queue)

    def _start_threads(self):
        """!

        @param client_id: The id of the client to be used.

        @return None
        """
        logger.debug10("Begin Function: %s %s %s", self.address,
                       self.available_ports[0], self.client_id)

        # TODO: Configure to connect to multiple available clients
        self.brokerclient.connect(self.address, self.available_ports[0],
                                  self.client_id)

        logger.debug("BrokerClient connected")

        self.brokerclient.start_thread(self.broker_queue)
        self.socket_server.start_thread(self.socket_recv_queue,
                                        self.socket_send_queue)

        logger.debug10("End Function")

    def _stop(self):
        """!
        Alias for _stop_thread
        """
        self._stop_thread()

    def _stop_thread(self):
        """!
        Stops the brokerclient thread.
        """
        logger.debug10("Begin Function")
        self.brokerclient.stop_thread()
        logger.debug10("End Function")
