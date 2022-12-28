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
import sys
import time

# 3rd Party libraries
from ibapi.client import Contract
from ibapi.order import Order

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients import broker
from pytrader.libs.clients.mysql import index_info

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
class Index():

    def __init__(self):
        logger.debug("Begin Function")
        self.ticker = None
        self.name = None
        self.ibkr_symbol = None
        self.ibkr_contract_id = None
        self.ibkr_primary_exchange = None
        self.yahoo_symbol = None
        self.ipo_date = None
        logger.debug("End Function")
        return None

    def __repr__(self):
        return logger.info("Index(Ticker: %s, Name: %s)", self.ticker,
                           self.name)

    def get_information(self, ticker=None):
        logger.debug("Begin Function")
        if self.ticker is None and ticker:
            self.set_information(ticker)
        logger.debug("End Function")
        return self

    def set_information(self, ticker):
        logger.debug("Begin Function")
        info = index_info.IndexInfo()
        where = "`ticker`='" + ticker + "'"
        item = info.select(where_clause=where)
        logger.debug("Index Info: %s", item)
        self.ticker = item[0]["ticker"]
        self.name = item[0]["name"]
        self.ibkr_symbol = item[0]["ibkr_symbol"]
        self.ibkr_contract_id = item[0]["ibkr_contract_id"]
        self.ibkr_primary_exchange = item[0]["ibkr_primary_exchange"]
        self.yahoo_symbol = item[0]["yahoo_symbol"]
        self.ipo_date = item[0]["ipo_date"]
        logger.debug("End Function")
        return None
