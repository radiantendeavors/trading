"""!@package pytrader.strategies.base

Provides the Base Class for a Strategy.

@author G. S. derber
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

@file pytrader/strategies/base.py

    Provides the Base Class for a Strategy

"""
# ==================================================================================================
#
# This file requires special pylint rules...
#
# C0302: too many lines
# R0904: too many public methods
#
# pylint: disable=C0302,R0904
#
# ==================================================================================================
import datetime
from multiprocessing import Queue

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
class BaseStrategy():
    """!
    The strategy class.

    Provides functionality required by strategies.
    """

    def __init__(self, cmd_queue: Queue, data_queue: Queue, next_order_id: int,
                 strategy_id: str) -> None:
        """!
        Initializes the strategy class.

        @param cmd_queue:
        @param data_queue:
        @param next_order_id:
        @param strategy_id

        @return None
        """
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.next_order_id = next_order_id
        self.strategy_id = strategy_id
        self.initializing = True

        self.time_now = datetime.datetime.now()

        self.security = []
        self.use_options = False
        self.quantity = 0
        self.num_strikes = 0
        self.bar_sizes = []
        self.days_to_expiration = 0

        self.contracts = {}
        self.bars = {}
        self.ticks = {}
        self.market_data = {}
        self.orders = {}
        self.order_ids = {}
        self.order_prices = {}

        self.expirations = {}
        self.all_strikes = {}
        self.strikes = {}

        self.long_position = []
        self.short_position = []
