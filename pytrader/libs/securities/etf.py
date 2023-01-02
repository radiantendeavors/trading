"""!
@package pytrader.libs.securities.etf

Provides the base class for an ETF

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


@file pytrader/libs/securities/etf.py
"""
# System libraries
import datetime
# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.mysql import etf_info
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
class Etf(securitybase.SecurityBase):
    """
    Etf

    Works with an ETF
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.req_id = 10000
        self.security_type = "STK"

    def __get_info_from_database(self):
        info = etf_info.EtfInfo()
        where_clause = "`ticker`='" + self.ticker_symbol + "'"
        return info.select(where_clause=where_clause)

    def update_info(self):
        logger.debug10("Begin Function")
        result = self.__get_info_from_database()

        logger.debug("Result: %s", result)

        if result[0]["ibkr_exchange"] == "SMART" and result[0][
                "ibkr_primary_exchange"]:
            self.primary_exchange = result[0]["ibkr_primary_exchange"]
            self.set_contract(self.ticker_symbol,
                              self.security_type,
                              primary_exchange=self.primary_exchange)
        else:
            self.set_contract(self.ticker_symbol, self.security_type)

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
        self.brokerclient.cancel_head_timestamp(req_id)
        ipo_date = datetime.datetime.strptime(data, "%Y%m%d-%H:%M:%S")
        logger.debug("Data: %s", ipo_date)

        db = etf_info.EtfInfo()
        db.update_ibkr_ipo_date(self.ticker_symbol, ipo_date)

        logger.debug10("End Function")
        return None
