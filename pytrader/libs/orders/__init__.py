"""!
@package pytrader.libs.orders

Provides order management.

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

@file pytrader/libs/orders/__init__.py
"""
from multiprocessing import Queue

from ibapi.contract import Contract
from ibapi.order import Order

from pytrader.libs.system import logging
from pytrader.libs.utilities.config import Config

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
class BaseOrder():
    """!
    Base Class for Orders
    """

    def __init__(self, data_queue: Queue, contract: Contract, strategy: str):
        self.contract = contract
        self.data_queue = data_queue
        self.order = Order()
        self.status = None
        self.strategy_id = strategy

    def get_order(self) -> Order:
        """!
        Returns the order
        """
        return self.order

    def get_status(self):
        """!
        Returns the order's status.
        """
        return self.status

    def get_parent_id(self) -> int:
        """!
        Returns the parent id of the order
        """
        return self.order.parentId

    def set_order(self, action: str, order_type: str, quantity: int, transmit: bool) -> None:
        """!
        Sets the basic order details

        @param action:
        @param order_type:
        @param quantity:
        @param transmit:

        @return None
        """
        self.order.action = action
        self.order.orderType = order_type
        self.order.totalQuantity = quantity
        self.order.transmit = transmit

        conf = Config()
        conf.read_config()
        self.order.account = conf.brokerclient_account

    def set_limit_order_price(self, price: float) -> None:
        """!
        Sets limit order prices.

        @param price:

        @return None
        """
        # Ensure we have a valid price for orders.
        price = round(price, 2)
        self.order.lmtPrice = price

    def set_order_id(self, order_id: int) -> None:
        """!
        Set's the order id for the order.

        @param order_id:

        @return None
        """
        self.order.orderId = order_id

    def set_order_type(self, order_type: str) -> None:
        """!
        Sets the order type.

        @param order_type:

        @return None
        """
        self.order.orderType = order_type

    def set_parent_order_id(self, order_id: int) -> None:
        """!
        Set's the parent order id.

        @param order_id:

        @return None
        """
        self.order.parentId = order_id

    def set_status(self, status: str) -> None:
        """!
        Sets the order status.

        @param status:

        @return None
        """
        self.status = status

    def set_stop_price(self, price: float) -> None:
        """!
        Sets the stop price for the order

        @param price:

        @return None
        """
        # Ensure we have a valid price for orders.
        price = round(price, 2)
        self.order.auxPrice = price


class Order(BaseOrder):
    """!
    Main Order Class
    """

    def send_order(self) -> None:
        """!
        Sends an order to the broker.

        @return None
        """
        message = {
            self.strategy_id: {
                "place_order": {
                    "order": self.order,
                    "contract": self.contract
                }
            }
        }
        logger.debug9("Sending order message: %s", message)
        self.data_queue.put(message)

    def send_order_cancel(self):
        """!
        Sends a cancellation request to the broker.

        @return None
        """
        message = {self.strategy_id: {"cancel_order": self.order.orderId}}
        self.data_queue.put(message)

    # def close_long_position(self, ticker, order_type=None, price=None):
    #     order = {
    #         "ticker": ticker,
    #         "order_type": order_type,
    #         "action": "SELL",
    #         "quantity": self.quantity
    #     }

    #     if order_type is None:
    #         order_type = "MKT"

    #     if price:
    #         order["price"] = price

    #     self._send_order(order)

    # def open_long_position(self,
    #                        ticker,
    #                        order_type,
    #                        price=None,
    #                        profit_target=None,
    #                        stop_loss=None):
    #     order = {
    #         "ticker": ticker,
    #         "order_type": order_type,
    #         "action": "BUY",
    #         "quantity": self.quantity
    #     }

    #     if price:
    #         order["price"] = price
    #     if profit_target:
    #         order["profit_target"] = profit_target
    #     if stop_loss:
    #         order["stop_loss"] = stop_loss

    #     self._send_order(order)
    #     self.long_position.append(ticker)

    #     logger.info("Buy %s order placed for %s", order_type,
    #                 ticker.localSymbol)
    #     logger.info("Quantity: %s", self.quantity)

    #     if price:
    #         logger.info("Price: %s", price)
    #     if profit_target:
    #         logger.info("Profit Target: %s", profit_target)
    #     if stop_loss:
    #         logger.info("Stop Loss: %s", stop_loss)

    # def open_short_position(self,
    #                         ticker,
    #                         order_type,
    #                         price=None,
    #                         profit_target=None,
    #                         stop_loss=None):
    #     order = {
    #         "ticker": ticker,
    #         "order_type": order_type,
    #         "action": "SELL",
    #         "quantity": self.quantity
    #     }

    #     if price:
    #         order["price"] = price
    #     if profit_target:
    #         order["profit_target"] = profit_target
    #     if stop_loss:
    #         order["stop_loss"] = stop_loss

    #     self._send_order(order)
    #     self.short_position.append(ticker)

    # def close_short_position(self, ticker, order_type=None, price=None):
    #     order = {
    #         "ticker": ticker,
    #         "order_type": order_type,
    #         "action": "BUY",
    #         "quantity": self.quantity
    #     }
    #     if order_type is None:
    #         order_type = "MKT"

    #     if price:
    #         order["price"] = price

    #     self._send_order(order)

    # def _send_order(self, order):
    #     message = {"place_order": order}
    #     self.cmd_queue.put(message)
