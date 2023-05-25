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
import datetime
import queue

from abc import ABCMeta, abstractmethod

# 3rd Party libraries
from ibapi import contract

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
class Bars(bars.BasicBars):
    """!
    Contains bar history for a security
    """

    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):

        ## Bar history length
        self.duration = None

        ## Bar contract
        self.contract = kwargs["contract"]

        ##
        self.queue = queue.Queue()

        super().__init__(*args, **kwargs)

    @abstractmethod
    def retrieve_bar_history(self):
        """!
        Requests bar history
        """
        raise NotImplementedError

    @abstractmethod
    def request_real_time_bars(self):
        """!
        Requests real time bars
        """
        raise NotImplementedError

    def send_bars(self, bar_type, bar_contract: contract.Contract, bars: list,
                  bar_size: str):
        """!
        Sends bar information to strategies.

        @param bar_type:
        @param bar_contract:
        @param bars:
        @param bar_size:

        @return None
        """
        message = {bar_type: {bar_contract.localSymbol: {bar_size: bars}}}
        self.data_queue.put(message)

    # ==============================================================================================
    #
    # Internal Use only functions.  These should not be used outside the class.
    #
    # ==============================================================================================
    def _retreive_broker_bar_history(self):
        logger.debug10("Begin Function")

        logger.debug4("Duration: %s", self.duration)
        if self.duration == "all":
            logger.debug4("Getting all history")
        else:
            req_id = self.brokerclient.req_historical_data(
                self.contract, self.bar_size, duration_str=self.duration)

        bar_list = self.brokerclient.get_data(req_id)

        # self.brokerclient.cancel_historical_data(req_id)
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
            logger.debug3("Setting Duration for Bar Size: %s", self.bar_size)
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
            logger.debug3("Duration Set to %s", self.duration)
        logger.debug10("End Function")
        return None
