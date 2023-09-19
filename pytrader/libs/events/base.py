"""!@package pytrader.libs.events.base

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

@file pytrader/libs/events/base.py
"""
# System Libraries
from abc import ABC, abstractmethod

# Application Libraries
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
class Subject(ABC):

    @abstractmethod
    def attach(self, observer) -> None:
        """!
        Adds an observer for the Event.
        """

    @abstractmethod
    def detach(self, observer) -> None:
        """!
        Removes and observer from the subject
        """

    @abstractmethod
    def notify(self) -> None:
        """!
        Notifies all observers about an event.
        """


class Observer(ABC):
    """!
    The Observer interface declares the update method used by subjects.
    """

    @abstractmethod
    def update(self, subject: Subject) -> None:
        """!
        Receives an update from the subject.
        """
