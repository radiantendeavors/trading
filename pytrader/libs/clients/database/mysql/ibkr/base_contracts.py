"""!
@package pytrader.libs.clients.mysql.etf_info

Provides the database client

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


@file pytrader/libs/clients/mysql/etf_info.py
"""
from datetime import date
from typing import Optional

# System Libraries
import pymysql

# Other Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.base import IbkrBase
# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging
from pytrader.libs.utilities import text

# 3rd Party Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)
colortext = text.ConsoleText()


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrBaseContracts(IbkrBase):

    table_name = None

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
