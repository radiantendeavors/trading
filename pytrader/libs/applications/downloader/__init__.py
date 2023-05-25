"""!@package pytrader.libs.applications.downloader

The main user interface for the trading program.

@author Geoff S. Derber
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

@file pytrader/libs/applications/downloader/__init__.py
"""
# System Libraries

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import contracts

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)

IBKR_ASSET_CLASS_MAP = {
    "stocks": "STK",
    "futures": "FUT",
    "options": "OPT",
    "indices": "IND",
    "futures_options": "FOP",
    "forex": "CASH",
    "combo": "BAG",
    "warrant": "WAR",
    "bond": "BOND",
    "commodity": "CMDTY",
    "news": "NEWS",
    "fund": "FUND"
}


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class DownloadProcess():

    def __init__(self, cmd_queue, data_queue):
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue

    def run(self, asset_classes, securities_list: list = []):
        if len(securities_list) == 0:
            logger.error("No security list set.")
            logger.error(
                "Automatic security list generation not implemented yet.")
        else:
            self.download_info(asset_classes, securities_list)

        while True:
            message = self.data_queue.get()
            self._process_message(message)

    def download_info(self, asset_classes, securities_list: list = []):
        """
        basic_info

        @param investments
        @param brokerclient
        @param security
        """
        logger.debug("Begin Function")

        for asset_class in asset_classes:
            sec_type = IBKR_ASSET_CLASS_MAP[asset_class]

            if securities_list:
                info = contracts.Contracts(self.cmd_queue, sec_type,
                                           securities_list)
            else:
                info = contracts.Contracts(self.cmd_queue, sec_type)

            info.update_info("broker")

        logger.debug("End Function")

    def download_bars(self,
                      investments,
                      brokerclient,
                      bar_sizes=None,
                      securities_list=None,
                      duration=None):
        logger.debug10("Begin Function")
        if securities_list:
            info = contracts.Contracts(brokerclient=brokerclient,
                                       securities_type=investments,
                                       securities_list=securities_list)
        else:
            info = contracts.Contracts(brokerclient=brokerclient,
                                       securities_type=investments)

        info.update_history("broker", bar_sizes, duration)
        logger.debug10("End Function")

    def _process_data(self, data):
        if data.get("contracts"):
            self.contracts = data["contracts"]
            logger.debug("Contracts: %s", self.contracts)
        # if data.get("option_details"):
        #     logger.debug("Processing Option Details")
        #     self._process_option_details(data["option_details"])
        # if data.get("bars"):
        #     logger.debug3("Processing Bars")
        #     self._process_bars(data["bars"])
        # if data.get("tick"):
        #     logger.debug3("Processing Tick Data")
        #     self._process_ticks(data["tick"])
