"""!@package pytrader.plugins.dbmgr.upgrade

Upgrades the database schema

@author Geoff S. Derber
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

@file pytrader/plugins/dbmgr/upgrade.py

Upgrades the database schema

"""

# System Libraries
# import os
# import sys

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.mysql import stock_info, ibkr_stock_info

# Conditional Libraries

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
# Functions
#
# ==================================================================================================
def upgrade(args):
    logger.debug10("Begin Function")
    info = stock_info.StockInfo()
    new_info = ibkr_stock_info.IbkrStockInfo()
    where = "`ibkr_contract_id` IS NOT NULL"
    securities = info.select(where_clause=where)

    for item in securities:
        new_info.insert(item['id'], item['ticker'], item['ibkr_contract_id'],
                        item['ibkr_primary_exchange'], item['ibkr_exchange'],
                        item['ipo_date'])

    logger.debug10("End Function")


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])

    cmd = subparsers.add_parser("upgrade",
                                aliases=["u"],
                                parents=parent_parsers,
                                help="Upgrades the database")

    cmd.set_defaults(func=upgrade)

    return cmd