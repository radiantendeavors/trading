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
from pytrader.libs.clients.database.mysql.ibkr.base_contracts import (
    IbkrBaseContracts, IbkrBaseNoHistory)
from pytrader.libs.system import logging

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
class IbkrIndexContracts(IbkrBaseContracts):
    """!
    Class for interacting with the Index Contracts Table.
    """
    table_name = "z_ibkr_ind_contracts"
    insert_column_names = [
        "contract_id", "symbol", "security_type", "exchange", "currency", "local_symbol"
    ]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrIndexContractDetails(IbkrBaseContracts):
    """!
    Class for interacting with the Index Contracts Details Table.
    """
    table_name = "z_ibkr_ind_contract_details"
    insert_column_names = [
        "ibkr_contract_id", "market_name", "min_tick", "price_magnifier", "long_name", "industry",
        "category", "subcategory", "timezone_id", "ev_multiplier", "agg_group", "market_rule_ids"
    ]
    update_column_names = insert_column_names


class IbkrIndexHistoryBeginDate(IbkrBaseContracts):
    """!
    Class for interacting with the Index Contracts History Begin Table.
    """
    table_name = "z_ibkr_ind_history_begin_date"
    insert_column_names = ["ibkr_contract_id", "oldest_datetime"]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrIndexLiquidHours(IbkrBaseContracts):
    """!
    Class for interacting with the Index Contracts Liquid Hours Table.
    """
    table_name = "z_ibkr_ind_liquid_hours"
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrIndexOptParams(IbkrBaseContracts):
    """!
    Class for interacting with the Index Contracts Options Parameters Table.
    """
    table_name = "z_ibkr_ind_option_parameters"
    insert_column_names = ["ibkr_contract_id", "exchange", "multiplier", "expirations", "strikes"]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrIndexTradingHours(IbkrBaseContracts):
    """!
    Class for interacting with the Index Contracts Trading Hours Table.
    """
    table_name = "z_ibkr_ind_trading_hours"
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrIndexNoHistory(IbkrBaseNoHistory):
    """!
    Class for interacting with the Index Contracts No History Table.
    """
    table_name = "z_ibkr_ind_no_history"
    insert_column_names = ["ibkr_contract_id"]
    update_column_names = insert_column_names + ["last_updated"]
