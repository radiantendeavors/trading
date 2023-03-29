"""!
@package pytrader.libs.bars

Provides Bar Data

@author G. S. Derber
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


@file pytrader/libs/bars/__init__.py
"""
# Standard libraries
import json
import queue

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import ticks

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
class BrokerTicks(ticks.BasicTicks):
    """!
    Contains bar history for a security
    """

    def __init__(self, *args, **kwargs):
        ## Broker Client
        self.brokerclient = None

        ## Bar history length
        self.duration = None

        ## Bar contract
        self.contract = kwargs["contract"]

        ## Socket Server
        self.data_queue = kwargs["data_queue"]

        logger.debug10("Begin Function")
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]

        if kwargs.get("duration"):
            if kwargs["duration"]:
                self.duration = kwargs["duration"]

        self.tick_req_id = None

        self.queue = queue.Queue()

        super().__init__(*args, **kwargs)

    def run(self):
        broker_connection = True
        while broker_connection:
            new_tick = self.queue.get()
            logger.debug3("New Tick: %s", new_tick)

            # Convert size from type Decimal to Float, because json can't work with Decimals
            new_tick[3] = float(new_tick[3])

            # Convert tickAttribLast to str
            new_tick[4] = str(new_tick[4])

            self.send_ticks(new_tick)
            broker_connection = self.brokerclient.is_connected()

    def request_ticks(self):
        self.tick_req_id = self.brokerclient.req_tick_by_tick_data(
            self.queue, self.contract)

    def send_ticks(self, tick):
        message = {"tick": {self.contract.symbol: tick}}
        self.data_queue.put(message)
