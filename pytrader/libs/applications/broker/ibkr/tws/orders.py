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

from multiprocessing import Queue

# 3rd Party Libraries
from ibapi import contract
from ibapi import order

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.broker import twsapi

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


# ==================================================================================================
#
# TWS Client
#
# ==================================================================================================
class Orders():

    def _create_braket_order(self, order_request):
        order_contract = order_request["contract"]
        self.next_order_id += 5

        parent_order = order.Order()
        parent_order.orderId = self.next_order_id
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
        stop_order.orderType = "TRAIL"
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

    def _create_order(self, order_request):
        order_contract = self.contracts[order_request["ticker"]]

        new_order = order.Order()
        new_order.action = order_request["action"]
        new_order.orderType = order_request["order_type"]
        new_order.quantity = order_request["quantity"]

        if order_request.get("price"):
            new_order.lmtPrice = order_request["price"]

        new_order.transmit = True

        self.brokerclient.place_order(order_contract, new_order)

    def _request_global_cancel(self):
        self.brokerclient.req_global_cancel()
