"""!
@package pytrader.libs.clients.broker.ibkr.tws.twsreal
Creates a basic interface for interacting with a broker

@file pytrader/libs/clients/broker/ibkr/tws/twsreal.py

Creates a basic interface for interacting with a broker

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

"""
# ==================================================================================================
#
# Pacing Violations
#
# 1. To avoid pacing violations, historical data can be requested no more than 60 requests in any 10
# minute period.
# 2. There are 600 seconds in 10 minutes.
# 3. Therefore, 1 request every 15 seconds to ensure we don't cross the threshold.
#
# https://interactivebrokers.github.io/tws-api/historical_limitations.html#pacing_violations
#
# ==================================================================================================
import datetime
import time
from typing import Optional

from pytrader.libs.clients.broker.ibkr.tws.thread import TwsThreadMngr
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
class TwsPacingMngr(TwsThreadMngr):
    """!
    The Command interface for the TWS API Client.
    """

    historical_data_req_timestamp = datetime.datetime(year=1970,
                                                      month=1,
                                                      day=1,
                                                      hour=0,
                                                      minute=0,
                                                      second=0)

    contract_details_data_req_timestamp = datetime.datetime(year=1970,
                                                            month=1,
                                                            day=1,
                                                            hour=0,
                                                            minute=0,
                                                            second=0)

    contract_history_begin_data_req_timestamp = datetime.datetime(year=1970,
                                                                  month=1,
                                                                  day=1,
                                                                  hour=0,
                                                                  minute=0,
                                                                  second=0)

    small_bar_data_req_timestamp = datetime.datetime(year=1970,
                                                     month=1,
                                                     day=1,
                                                     hour=0,
                                                     minute=0,
                                                     second=0)

    __historical_data_sleep_time = 0
    __contract_details_sleep_time = 0
    __contract_history_begin_count = 0
    __contract_history_begin_sleep_time = 30
    __small_bar_sleep_time = 15
    __small_bar_sizes = ["1 secs", "5 secs", "10 secs", "15 secs", "30 secs"]
    __intraday_bar_sizes = __small_bar_sizes + [
        "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "20 mins", "30 mins", "1 hour",
        "2 hours", "3 hours", "4 hours", "8 hours"
    ]
    __bar_sizes = __intraday_bar_sizes + ["1 day", "1 week", "1 month"]

    def contract_details_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.contract_details_data_req_timestamp,
                        self.__contract_details_sleep_time)

    def contract_history_begin_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.contract_history_begin_data_req_timestamp,
                        self.__contract_history_begin_sleep_time)

    def historical_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.historical_data_req_timestamp, self.__historical_data_sleep_time)

    def small_bar_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.small_bar_data_req_timestamp, self.__small_bar_sleep_time)

    # ==============================================================================================
    #
    # Internal Helper Functions
    #
    # ==============================================================================================
    def _data_wait(self, timestamp, sleep_time):
        time_diff = datetime.datetime.now() - timestamp

        while time_diff.total_seconds() < sleep_time:

            logger.debug6("Now: %s", datetime.datetime.now())
            logger.debug6("Last Request: %s", timestamp)
            logger.debug6("Time Difference: %s seconds", time_diff.total_seconds())
            remaining_sleep_time = sleep_time - time_diff.total_seconds()
            logger.debug6("Sleep Time: %s", remaining_sleep_time)
            time.sleep(sleep_time - time_diff.total_seconds())
            time_diff = datetime.datetime.now() - timestamp

    def _calculate_deep_data_allotment(self):
        """!
        Caclulates the allowed dep data requests available.
        """
        min_allotment = 3
        max_allotment = 60

        basic_allotment = self.__available_market_data_lines % 100

        if basic_allotment < min_allotment:
            self.__available_deep_data_allotment = min_allotment
        elif basic_allotment > max_allotment:
            self.__available_deep_data_allotment = max_allotment
        else:
            self.__available_deep_data_allotment = basic_allotment
