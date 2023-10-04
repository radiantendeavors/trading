"""!
@package pytrader.libs.clients.database.mysql.ibkr.stk_opt_contracts

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


@file pytrader/libs/clients/database/mysql/ibkr/stk_opt_contracts.py
"""
from datetime import date, timedelta
from typing import Optional

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
class IbkrStkOptContracts(IbkrBaseContracts):
    table_name = "z_ibkr_stk_opt_contracts"
    insert_column_names = [
        "contract_id", "symbol", "security_type", "last_trading_date", "strike", "opt_right",
        "multiplier", "exchange", "currency", "local_symbol", "trading_class"
    ]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrStkOptContractDetails(IbkrBaseContracts):
    table_name = "z_ibkr_stk_opt_contract_details"
    insert_column_names = [
        "ibkr_contract_id", "market_name", "min_tick", "price_magnifier", "order_types",
        "valid_exchanges", "underlying_contract_id", "contract_month", "timezone_id",
        "ev_multiplier", "agg_group", "sec_id_list", "market_rule_ids", "real_expiration_date",
        "last_trade_time"
    ]
    update_column_names = insert_column_names

    def insert(self, columns: list, additional_criteria: Optional[dict] = None) -> None:
        if columns[-1] == "":
            columns[-1] = None
        super().insert(columns, additional_criteria)


class IbkrStkOptInvalidContracts(IbkrBaseContracts):
    table_name = "z_ibkr_stk_opt_invalid_contracts"
    insert_column_names = ["symbol", "last_trading_date", "strike", "opt_right"]
    update_column_names = insert_column_names + ["last_updated"]

    def clean_invalid(self):
        self._clean_last_updated()
        self._clean_expired()

    def _clean_last_updated(self):
        today = date.today()
        num_days = timedelta(days=7)
        last_update_min = today - num_days
        criteria = {"last_updated": last_update_min}

        self.delete(criteria)

    def _clean_expired(self):
        today = date.today()
        criteria = {"last_trading_date": today}
        self.delete(criteria)


class IbkrStkOptHistoryBeginDate(IbkrBaseContracts):
    table_name = "z_ibkr_stk_opt_history_begin_date"
    insert_column_names = ["ibkr_contract_id", "oldest_datetime"]
    update_column_names = insert_column_names + ["last_updated"]

    def clean_history(self):
        self._clean_last_updated()

    def _clean_last_updated(self):
        today = date.today()
        num_days = timedelta(days=7)
        last_update_min = today - num_days
        criteria = {"last_updated": last_update_min}

        self.delete(criteria)


class IbkrStkOptLiquidHours(IbkrBaseContracts):
    table_name = "z_ibkr_stk_opt_liquid_hours"
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrStkOptTradingHours(IbkrBaseContracts):
    table_name = "z_ibkr_stk_opt_trading_hours"
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrStkOptNoHistory(IbkrBaseContracts):
    table_name = "z_ibkr_stk_opt_no_history"
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
