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
from pytrader.libs.clients.mysql import stock_info
from pytrader.libs import securities
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
class Stocks(securities.Securities):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.investment_type = "stocks"
        return None

    def get_list(self):
        info = stock_info.StockInfo()
        where = "`delisted_date` IS NULL"
        self.securities_list = info.select(where_clause=where)
        return self.securities_list
