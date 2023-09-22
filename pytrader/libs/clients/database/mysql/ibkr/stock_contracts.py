"""!
@package pytrader.libs.clients.database.mysql.ibkr_stock_contracts

Provides the database client

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


@file pytrader/libs/clients/mysql/etf_info.py
"""
# System Libraries
from datetime import date

# 3rd Party Libraries
import pymysql

# Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.base_contracts import \
    IbkrBaseContracts
from pytrader.libs.system import logging
from pytrader.libs.utilities import text

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrStockContracts(IbkrBaseContracts):

    table_name = "z_ibkr_stock_contracts"
    insert_column_names = [
        "contract_id", "ticker_symbol", "security_type", "exchange", "currency", "local_symbol",
        "primary_exchange", "trading_class"
    ]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrStockContractDetails(IbkrBaseContracts):
    table_name = "z_ibkr_stock_contract_details"
    insert_column_names = [
        "ibkr_contract_id", "market_name", "min_tick", "price_magnifier", "long_name", "industry",
        "category", "subcategory", "timezone_id", "stock_type", "aggregated_group"
    ]
    update_column_names = insert_column_names


class IbkrStockExchanges(IbkrBaseContracts):
    table_name = "z_ibkr_stock_exchanges"
    insert_column_names = ["ibkr_contract_id", "exchange"]
    update_column_names = insert_column_names


class IbkrStockHistoryBeginDate(IbkrBaseContracts):
    table_name = "z_ibkr_stock_history_begin_date"
    insert_column_names = ["ibkr_contract_id", "oldest_datetime"]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrStockLiquidHours(IbkrBaseContracts):
    table_name = "z_ibkr_stock_liquid_hours"
    insert_column_names = ["ibkr_contract_id", "liquid_hours"]
    update_column_names = insert_column_names


class IbkrStockOrderTypes(IbkrBaseContracts):
    table_name = "z_ibkr_stock_order_types"
    insert_column_names = ["ibkr_contract_id", "order_type"]
    update_column_names = insert_column_names


class IbkrStockTradingHours(IbkrBaseContracts):
    table_name = "z_ibkr_stock_liquid_hours"
    insert_column_names = ["ibkr_contract_id", "trading_hours"]
    update_column_names = insert_column_names
