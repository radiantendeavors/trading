"""!
@package pytrader.libs.bars

Provides Bar Data

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


@file pytrader/libs/bars/__init__.py
"""
# Standard libraries
import datetime
import json

# 3rd Party libraries
import pandas

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import bars

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
class BrokerBars(bars.BasicBars):
    """!
    Contains bar history for a security
    """

    def __init__(self, *args, **kwargs):
        ## Broker Client
        self.brokerclient = None

        ## Bar history length
        self.duration = None

        ## List of Long Duration Bar Sizes
        self.bar_size_long_duration = ["1 day", "1 week", "1 month"]

        ## Bar contract
        self.contract = kwargs["contract"]

        ## Socket Server
        self.socket_queue = kwargs["socket_queue"]

        logger.debug10("Begin Function")
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]

        if kwargs.get("duration"):
            if kwargs["duration"]:
                self.duration = kwargs["duration"]

        self.rtb_req_id = None

        super().__init__(*args, **kwargs)

    def run(self):
        broker_connection = True
        while broker_connection:
            real_time_bar = self.brokerclient.rtb_queue[self.rtb_req_id].get()

            bar_datetime = datetime.datetime.fromtimestamp(
                real_time_bar[0]).strftime('%Y%m%d %H:%M:%S')
            bar_datetime_str = str(bar_datetime) + " EST"

            real_time_bar[0] = bar_datetime_str
            real_time_bar[5] = int(real_time_bar[5])
            real_time_bar[6] = float(real_time_bar[6])
            self.send_bars("real_time_bars", real_time_bar)
            broker_connection = self.brokerclient.is_connected()

    def retrieve_bar_history(self):
        logger.debug10("Begin Function")
        if self.bar_size == "rtb":
            logger.error("Invalid Bar Size for History")
        else:
            logger.debug("Duration: %s", self.duration)
            self._set_duration()
            logger.debug("Duration: %s", self.duration)

            if self.brokerclient:
                self._retreive_broker_bar_history()
            else:
                raise NotImplementedError

        logger.debug10("End Function")

    def request_real_time_bars(self):
        if self.bar_size == "rtb":
            self.rtb_req_id = self.brokerclient.req_real_time_bars(
                self.contract)
        else:
            logger.error("Invalid Bar Size for real time bars")

    def send_bars(self, bar_type, bars):
        msg = {bar_type: {self.contract.symbol: {self.bar_size: bars}}}
        message = json.dumps(msg)
        self.socket_queue.put(message)

    # ==============================================================================================
    #
    # Internal Use only functions.  These should not be used outside the class.
    #
    # ==============================================================================================
    def _retreive_broker_bar_history(self):
        logger.debug("Duration: %s", self.duration)

        if self.duration == "all":
            logger.debug("Getting all history")
            #if self.bar_size not in self.bar_size_long_duration:
            #for

        else:
            req_id = self.brokerclient.req_historical_data(
                self.contract, self.bar_size, duration_str=self.duration)

        bar_list = self.brokerclient.get_data(req_id)
        logger.debug4("Bar List: %s", bar_list)

        for bar in bar_list:
            logger.debug3("Bar: %s", bar)
            bar_date = bar.date
            bar_open = bar.open
            bar_high = bar.high
            bar_low = bar.low
            bar_close = bar.close
            bar_volume = float(bar.volume)
            #bar_wap = bar.wap
            bar_count = bar.barCount

            self.bar_list.append([
                bar_date, bar_open, bar_high, bar_low, bar_close, bar_volume,
                bar_count
            ])

        self.send_bars("bars", self.bar_list)
        logger.debug10("End Function")

    def _set_duration(self):
        logger.debug10("Begin Function")
        if self.duration is None:
            logger.debug("Setting Duration for Bar Size: %s", self.bar_size)
            if self.bar_size == "1 month":
                self.duration = "2 Y"
            elif self.bar_size == "1 week":
                self.duration = "1 Y"
            elif self.bar_size == "1 day":
                self.duration = "1 Y"
            elif self.bar_size == "1 hour":
                self.duration = "7 W"
            elif self.bar_size == "30 mins":
                self.duration = "4 W"
            elif self.bar_size == "15 mins":
                self.duration = "10 D"
            elif self.bar_size == "5 mins":
                self.duration = "4 D"
            elif self.bar_size == "1 min":
                self.duration = "2 D"
            logger.debug("Duration Set to %s", self.duration)
        logger.debug10("End Function")
        return None
