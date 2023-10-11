"""!
@package pytrader.libs.clients.database.mysql.ibkr.contract_universe

Interface to the 'z_ibkr_contract_listing' table.

@author G S Derber
@date 2022-2023
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


@file pytrader/libs/clients/database/mysql/ibkr/contract_universe.py
"""
from datetime import date

import pymysql

from pytrader.libs.clients.database.mysql.ibkr import base
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrContractUniverse(base.IbkrBase):
    """!
    Works with the 'z_ibkr_contract_listing' table.
    """
    table_name = "z_ibkr_contract_listing"
    insert_column_names = [
        "long_id", "ib_symbol", "product_description", "symbol", "currency", "asset_class",
        "exchange"
    ]
    update_column_names = insert_column_names + ["last_seen"]

    def max_date(self) -> date | None:
        """!
        Returns the max date in the database.

        @return date | None
        """
        sql = (f"SELECT MAX(`last_seen`) AS `max_date`\n"
               f"FROM {self.table_name}")

        try:
            self._execute(sql)
            data = self.mycursor.fetchone()
            return data["max_date"]

        except pymysql.Error as msg:
            logger.error("Error: %s", msg)
            return None
