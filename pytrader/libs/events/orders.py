"""!@package pytrader.libs.events.orders

The main user interface for the trading program.

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

@file pytrader/libs/events/orders.py
"""
from typing import List

from pytrader.libs.events.base import Observer, Subject
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
class OrderData(Subject):
    """!
    Order Data Subject.
    """
    _observers: List[Observer] = []
    valid_order_ids = []
    order_id = None
    order_status = {}

    def __init__(self):
        self.brokerclient = None

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None) -> None:
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)


class OrderIdData(Subject):
    """!
    Order Id Subject
    """
    _observers: List[Observer] = []
    order_id = None

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None) -> None:
        for observer in self._observers:
            if modifier != observer:
                observer.update(self)
