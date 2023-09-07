#!/usr/bin/env python3
"""!@package pytrader.ui.pytrdatabase

The user interface for managing the databases

@author G S Derber
@version HEAD
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

@file pytrader/ui/pytrdatabase.py

"""
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.clients import database
from pytrader.libs.system import logging

# Application Libraries

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
class DatabaseManager():
    """!
    Manages the database.
    """
    database_status = None

    def initialize_database(self) -> None:
        """!
        Initializes the database."""
        db = database.Database()
        db.create_engine()
        db_session = db.create_session()
        db.create_tables()
        logger.debug("Initialization Complete!")

    def check_database_status(self):
        """!
        Checks and updates the database status.

        Changes database_status to one of:
          - NOTEXIST
          - REQUIRESUPGRADE
          - GOOD
        """
        logger.debug("Check database status")

    def run(self):
        self.check_database_status()

        match self.database_status:
            case "NOTEXIST":
                self.initialize_database()
            case "REQUIRESUPGRADE":
                self.upgrade_database()
            case "GOOD":
                logger.debug("Database is Good, doing nothing")
            case _:
                logger.error("Something didn't work!")

    def upgrade_database(self):
        logger.debug10("Begin Function")
        # info = stock_info.StockInfo()
        # new_info = ibkr_stock_info.IbkrStockInfo()
        # where = "`ibkr_contract_id` IS NOT NULL"
        # securities = info.select(where_clause=where)

        # for item in securities:
        #     new_info.insert(item['id'], item['ticker'], item['ibkr_contract_id'],
        #                     item['ibkr_primary_exchange'], item['ibkr_exchange'],
        #                     item['ipo_date'])

        logger.debug10("End Function")

# ==================================================================================================
#
# Functions
#
# ==================================================================================================
