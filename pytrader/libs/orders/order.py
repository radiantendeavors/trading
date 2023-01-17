"""!
@package pytrader.libs.security

Provides the broker client

@author Geoff S. derber
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


@file security.py
"""
# System libraries
import sys
import time

# 3rd Party libraries
from ibapi.order import Order

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Order():

    def __init__(self):
        logger.debug("Begin Function")

    def place_order(self,
                    contract,
                    action,
                    order_type,
                    order_price=None,
                    quantity=1.0,
                    time_in_force="DAY",
                    transmit=False):
        self.req_id += 1

        logger.debug("BrokerClient.place_order")
        logger.debug("Security: %s", contract.symbol)
        logger.debug("Action: %s", action)
        logger.debug("Order Type: %s", order_type)
        logger.debug("Order Price: %s", order_price)
        logger.debug("Quantity: %s", quantity)
        logger.debug("Time in Force: %s", time_in_force)
        logger.debug("Transmit: %s", transmit)

        # Define limit order
        order = Order()
        order.action = action
        order.totalQuantity = quantity
        order.orderType = order_type
        order.tif = time_in_force

        if order_type == "LMT":
            order.lmtPrice = order_price

        order.transmit = transmit

        time.sleep(10)

        logger.debug("Contract: %s", contract)
        logger.debug("Order: %s", order)

        if self.nextValidOrderId:
            logger.info("Order IDs: %s", self.nextValidOrderId)
            self.placeOrder(self.nextValidOrderId, contract, order)
            time.sleep(5)

            logger.debug("Requesting Open Orders")
            self.reqOpenOrders()
            time.sleep(20)
            logger.debug("Requesting All Open Orders")
            self.reqAllOpenOrders()
            time.sleep(30)
        else:
            logger.error("Order ID not received.  Ending application.")
            sys.exit()
