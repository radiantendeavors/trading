"""!
@package pytrader.libs.orders

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

# 3rd Party libraries
from ibapi import order

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
class OrderBase():

    def __init__(self, *args, **kwargs):
        logger.debug10("Begin Function")
        logger.debug("Kwargs: %s", kwargs)
        self.brokerclient = kwargs["brokerclient"]
        self.order = order.Order()
        self.order.action = kwargs["action"]
        self.order.totalQuantity = kwargs["quantity"]
        self.order.transmit = kwargs["transmit"]
        logger.debug10("End Function")

    def __str__(self):
        logger.debug10("Begin Function")
        string_ = "Order Action: " + self.order.action + "\n"
        string_ += "Order Type: " + self.order.orderType + "\n"
        string_ += "Order Quantity: " + str(self.order.totalQuantity) + "\n"
        logger.debug("Order Action: %s", self.order.action)
        logger.debug("Order Type: %s", self.order.orderType)
        logger.debug("Order Quantity: %s", self.order.totalQuantity)

        if self.order.lmtPrice:
            string_ += "Limit Price: " + str(self.order.lmtPrice) + "\n"
            logger.debug("Limit Price: %s", self.order.lmtPrice)

        string_ += "Transmit Order: " + str(self.order.transmit)
        logger.debug("Transmit Order: %s", self.order.transmit)
        logger.debug10("End Function, returning:\n %s", string_)
        return string_

    def get_order(self):
        return self.order

    def place_order(self, contract):
        logger.debug10("Begin Function")
        self.order_id = self.brokerclient.place_order(contract, self.order)
        logger.debug("Order Placed, order id is: %s", self.order_id)
        logger.debug10("End Function")
        return self.order_id
