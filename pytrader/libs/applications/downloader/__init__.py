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
from pytrader.libs import securities

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

"""
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class DownloadProcess():

    def download_info(self, investments, brokerclient, securities_list=None):
        """
        basic_info

        @param investments
        @param brokerclient
        @param security
        """
        logger.debug("Begin Function")

        if securities:
            info = securities.Securities(brokerclient=brokerclient,
                                         securities_type=investments,
                                         securities_list=securities_list)
        else:
            info = securities.Securities(brokerclient=brokerclient,
                                         securities_type=investments)

        info.update_info(source="broker")

        logger.debug("End Function")

    def download_bars(self,
                      investments,
                      brokerclient,
                      bar_sizes=None,
                      securities_list=None,
                      duration=None):
        logger.debug10("Begin Function")
        if securities:
            info = securities.Securities(brokerclient=brokerclient,
                                         securities_type=investments,
                                         securities_list=securities_list)
        else:
            info = securities.Securities(brokerclient=brokerclient,
                                         securities_type=investments)

        info.update_history("broker", bar_sizes, duration)
        logger.debug10("End Function")