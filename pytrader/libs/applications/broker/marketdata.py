"""!
@package pytrader.libs.applications.broker.marketdata

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


@file pytrader/libs/applications/broker/marketdata.py
"""
# Standard libraries
import json
import queue

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import marketdata

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
class BrokerMarketData(marketdata.BasicMktData):
    """!
    Contains bar history for a security
    """

    def __init__(self, *args, **kwargs):
        ## Broker Client
        self.brokerclient = None

        ## Bar contract
        self.contract = kwargs["contract"]

        ## Socket Server
        self.data_queue = kwargs["data_queue"]

        logger.debug10("Begin Function")
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]

        self.market_data_req_id = None

        self.queue = queue.Queue()

        super().__init__(*args, **kwargs)

    def run(self):
        broker_connection = True
        while broker_connection:
            new_tick = self.queue.get()
            logger.debug3("New Tick: %s", new_tick)

            if new_tick[0] == "tick_price":
                # Convert tickAttribLast to str
                new_tick[3] = str(new_tick[3])
                self.send_ticks(new_tick)

            broker_connection = self.brokerclient.is_connected()

    def request_market_data(self):
        self.market_data_req_id = self.brokerclient.req_market_data(
            self.queue, self.contract)

    def send_ticks(self, tick):
        message = {"market_data": {self.contract.localSymbol: tick}}
        self.data_queue.put(message)
