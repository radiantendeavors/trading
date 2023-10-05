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
from datetime import date, timedelta

# 3rd Party Libraries
import pymysql

# Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.base_contracts import \
    IbkrBaseContracts
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

    table_name = "z_ibkr_ind_contracts"
    insert_column_names = [
        "contract_id", "symbol", "security_type", "exchange", "currency", "local_symbol"
    ]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrIndexContractDetails(IbkrBaseContracts):
    table_name = "z_ibkr_ind_contract_details"
    insert_column_names = [
        "ibkr_contract_id", "market_name", "min_tick", "price_magnifier", "long_name", "industry",
        "category", "subcategory", "timezone_id", "ev_multiplier", "agg_group", "market_rule_ids"
    ]
    update_column_names = insert_column_names


class IbkrIndexExchanges(IbkrBaseContracts):
    table_name = "z_ibkr_ind_exchanges"
    insert_column_names = ["ibkr_contract_id", "exchange"]
    update_column_names = insert_column_names


class IbkrIndexHistoryBeginDate(IbkrBaseContracts):
    table_name = "z_ibkr_ind_history_begin_date"
    insert_column_names = ["ibkr_contract_id", "oldest_datetime"]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrIndexLiquidHours(IbkrBaseContracts):
    table_name = "z_ibkr_ind_liquid_hours"
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrIndexOptParams(IbkrBaseContracts):
    table_name = "z_ibkr_ind_option_parameters"
    insert_column_names = ["ibkr_contract_id", "exchange", "multiplier", "expirations", "strikes"]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrIndexTradingHours(IbkrBaseContracts):
    table_name = "z_ibkr_ind_trading_hours"
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrIndexNoHistory(IbkrBaseContracts):
    table_name = "z_ibkr_ind_no_history"
    insert_column_names = ["ibkr_contract_id"]
    update_column_names = insert_column_names + ["last_updated"]

    def clean_history(self):
        self._clean_last_updated()

    def _clean_last_updated(self):
        today = date.today()
        num_days = timedelta(days=7)
        last_update_min = today - num_days
        criteria = {"last_updated": last_update_min}

        self.delete(criteria)
