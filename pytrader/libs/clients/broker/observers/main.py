"""!
@package pytrader.libs.applications.broker.observers.downloader

Provides the observer classes for the DownloaderProcess

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

@file pytrader/libs/applications/broker/observers/downloader.py
"""
# System Libraries

# 3rd Party Libraries

# Application Libraries
from pytrader.libs.clients.broker.observers.base import OrderIdObserver
from pytrader.libs.events import Subject
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
class MainOrderIdObserver(OrderIdObserver):
    """!
    Main Observer for Order Ids
    """

    def update(self, subject: Subject) -> None:
        """!
        Sends order ids to the main process

        @param subject:

        @return None
        """
        msg = {"next_order_id": subject.order_id}
        self.msg_queue.put(msg)
