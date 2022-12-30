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

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.mysql import etf_info
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
class Etf(security.Security):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.req_id = 10000
        self.security_type = "STK"

    def update_info(self):
        logger.debug10("Begin Function")
        info = etf_info.EtfInfo()
        where_clause = "`ticker`='" + self.ticker_symbol + "'"
        result = info.select(where_clause=where_clause)

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

        logger.debug10("End Function")
        return None
