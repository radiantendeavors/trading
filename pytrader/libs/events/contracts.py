"""!@package pytrader.libs.events.contracts

Provides Observers of Bar Data

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

@file pytrader/libs/events/contracts.py
"""
# System Libraries
from typing import List

# Application Libraries
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
class ContractData(Subject):
    """!
    Contract Data Base Class
    """

    _observers: List[Observer] = []
    contract = None

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


class ContractHistoryBeginDate(Subject):
    """!
    Used for updating History Begin Date information for contracts.
    """
    _observers: List[Observer] = []
    history_begin_ids = {}
    history_begin_date = {}
    req_id = 0

    def __repr__(self) -> str:
        class_name = type(self).__name__

        msg_ids = "  Ids:\n"
        dates = "  Dates:\n"

        for key, value in self.history_begin_ids.items():
            msg_ids += f"    {key}: {value}\n"

        for key, value in self.history_begin_date.items():
            dates += f"    {key}: {value}\n"
        message = (f"\n{class_name}(Subject) ({hex(id(self))}):(\n"
                   f"  Observers: {self._observers}\n"
                   f"{msg_ids}"
                   f"{dates}"
                   f"  Req Id: {self.req_id}\n"
                   f"  Number of Ids: 0\n)")
        return message

    def print_instance_attributes(self):
        for attribute, value in self.__dict__.items():
            msg = f"{attribute} = {value}"
            logger.warning(msg)

    def add_ticker(self, req_id: int, ticker: str) -> None:
        """!
        Adds a ticker for tracking.

        @param req_id:
        @param ticker:

        @return None
        """
        self.history_begin_ids[req_id] = ticker

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, modifier=None) -> None:
        for observer in self._observers:
            if modifier != observer:
                logger.debug(self.history_begin_ids)
                observer.update(self)


class ContractOptionParametrsData(Subject):
    """!
    Used for updating History Begin Date information for contracts.
    """
    _observers: List[Observer] = []
    req_ids = {}
    option_parameters = {}
    req_id = 0

    def add_ticker(self, req_id: int, ticker: str) -> None:
        """!
        Adds a ticker for tracking.

        @param req_id:
        @param ticker:

        @return None
        """
        self.req_ids[req_id] = ticker

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
