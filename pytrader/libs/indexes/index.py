"""!
@package pytrader.libs.indexes

Provides Market Index Information

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


@file security.py
"""
# System libraries

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients.mysql import index_info
from pytrader.libs.securities import security

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
class Index(security.Security):

    def __init__(self, *args, **kwargs):
        logger.debug("Begin Function")
        self.req_id = 30000
        self.security_type = "IND"
        super().__init__(*args, **kwargs)
        logger.debug("End Function")
        return None

    def __repr__(self):
        return logger.info("Index(Ticker: %s, Name: %s)", self.ticker,
                           self.name)

    def update_info(self):
        info = index_info.IndexInfo()
        where_clause = "`ticker`='" + self.ticker_symbol + "'"
        result = info.select(where_clause=where_clause)

        logger.debug("Result: %s", result)
