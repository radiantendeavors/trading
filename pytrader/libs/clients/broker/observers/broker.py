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

# Other Application Libraries
from pytrader.libs.clients.broker.observers.base import (BarDataObserver,
                                                         ContractDataObserver,
                                                         MarketDataObserver,
                                                         OrderDataObserver,
                                                         OrderIdObserver,
                                                         RealTimeBarObserver)
from pytrader.libs.events import Subject
# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

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
class BrokerOrderIdObserver(OrderIdObserver):
    """!
    Observer for historical bar data.
    """

    def update(self, subject: Subject) -> None:
        """!
        Saves the historical bar data to the database.
        """
        msg = {"next_order_id": subject.order_id}
        self.msg_queue.put(msg)
