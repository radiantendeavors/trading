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
import datetime
# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients.mysql import index_info
from pytrader.libs.securities import securitybase

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
class Index(securitybase.SecurityBase):

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

    def __get_info_from_database(self):
        info = index_info.IndexInfo()
        where_clause = "`ticker`='" + self.ticker_symbol + "'"
        return info.select(where_clause=where_clause)

    def update_info(self):
        result = self.__get_info_from_database()

        logger.debug("Result: %s", result)

        self.exchange = result[0]["ibkr_exchange"]
        logger.debug("Exchange: %s", self.exchange)
        self.set_contract(self.ticker_symbol,
                          self.security_type,
                          exchange=self.exchange)

        logger.debug("Get Security Data")
        req_id = self.brokerclient.get_security_data(self.contract)
        logger.debug("Request ID: %s", req_id)
        data = self.brokerclient.get_data(req_id)
        logger.debug("Data: %s", data)

        self.update_ipo_date()
        logger.debug10("End Function")
        return None

    def update_ipo_date(self):
        logger.debug10("Begin Function")
        result = self.__get_info_from_database()

        self.exchange = result[0]["ibkr_exchange"]
        logger.debug("Exchange: %s", self.exchange)
        self.set_contract(self.ticker_symbol,
                          self.security_type,
                          exchange=self.exchange)

        logger.debug("Get Security Data")
        req_id = self.brokerclient.get_ipo_date(self.contract)
        logger.debug("Request ID: %s", req_id)
        data = self.brokerclient.get_data(req_id)
        ipo_date = datetime.datetime.strptime(data, "%Y%m%d-%H:%M:%S")
        logger.debug("Data: %s", ipo_date)

        db = index_info.IndexInfo()
        db.update_ibkr_ipo_date(self.ticker_symbol, ipo_date)

        logger.debug10("End Function")
        return None
