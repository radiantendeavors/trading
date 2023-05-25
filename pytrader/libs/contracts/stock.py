"""!
@package pytrader.libs.security

Provides the broker client

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

# Other Application Libraries
from pytrader.libs.clients.mysql import stock_info
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
class Stock(securitybase.SecurityBase):

    def __init__(self, *args, **kwargs):
        self.req_id = 20000
        self.security_type = "STK"
        super().__init__(*args, **kwargs)

    def __get_info_from_database(self):
        info = stock_info.StockInfo()
        where_clause = "`ticker`='" + self.ticker_symbol + "'"
        return info.select(where_clause=where_clause)

    def update_ipo_date(self):
        logger.debug10("Begin Function")
        result = self.__get_info_from_database()

        if result[0]["ibkr_exchange"] == "SMART" and result[0][
                "ibkr_primary_exchange"]:
            self.primary_exchange = result[0]["ibkr_primary_exchange"]
            self.set_contract(self.ticker_symbol,
                              self.security_type,
                              primary_exchange=self.primary_exchange)
        else:
            self.set_contract(self.ticker_symbol, self.security_type)

        logger.debug("Get Security Data")
        req_id = self.brokerclient.get_ipo_date(self.contract)
        logger.debug("Request ID: %s", req_id)
        data = self.brokerclient.get_data(req_id)
        ipo_date = datetime.datetime.strptime(data, "%Y%m%d-%H:%M:%S")
        logger.debug("Data: %s", ipo_date)

        db = stock_info.StockInfo()
        db.update_ibkr_ipo_date(self.ticker_symbol, ipo_date)

        logger.debug10("End Function")
        return None
