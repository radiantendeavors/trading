"""!
@package pytrader.libs.clients.database.mysql.ibkr.option_contracts

Provides common functionality for all Option Contracts

@author G S derber
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


@file pytrader/libs/clients/database/mysql/ibkr/option_contracts.py
"""
from datetime import date, timedelta
from typing import Optional

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
class IbkrOptionContracts(IbkrBaseContracts):
    """!
    Class for interacting with the Stock Options Contracts Table.
    """
    insert_column_names = [
        "contract_id", "symbol", "security_type", "last_trading_date", "strike", "opt_right",
        "multiplier", "exchange", "currency", "local_symbol", "trading_class"
    ]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrOptionContractDetails(IbkrBaseContracts):
    """!
    Class for interacting with the Stock Options Contracts Details Table.
    """
    insert_column_names = [
        "ibkr_contract_id", "market_name", "min_tick", "price_magnifier", "order_types",
        "valid_exchanges", "underlying_contract_id", "contract_month", "timezone_id",
        "ev_multiplier", "agg_group", "sec_id_list", "market_rule_ids", "real_expiration_date",
        "last_trade_time"
    ]
    update_column_names = insert_column_names

    def insert(self, columns: list, additional_criteria: Optional[dict] = None) -> None:
        """!
        Inserts data into the table.

        @param columns:
        @param additional_criteria

        @return None
        """
        if columns[-1] == "":
            columns[-1] = None
        super().insert(columns, additional_criteria)


class IbkrOptionInvalidContracts(IbkrBaseContracts):
    """!
    Class for interacting with the Stock Options Invalid Contracts Table.
    """
    insert_column_names = ["symbol", "last_trading_date", "strike", "opt_right"]
    update_column_names = insert_column_names + ["last_updated"]

    def clean_invalid(self):
        """!
        Cleans table of old data.

        @return None
        """
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


class IbkrOptionHistoryBeginDate(IbkrBaseContracts):
    """!
    Class for interacting with the Stock Options History Begin Table.
    """
    insert_column_names = ["ibkr_contract_id", "oldest_datetime"]
    update_column_names = insert_column_names + ["last_updated"]

    def clean_history(self):
        """!
        Cleans old data from table.

        @return None
        """
        self._clean_last_updated()

    def _clean_last_updated(self):
        today = date.today()
        num_days = timedelta(days=7)
        last_update_min = today - num_days
        criteria = {"last_updated": last_update_min}

        self.delete(criteria)


class IbkrOptionLiquidHours(IbkrBaseContracts):
    """!
    Class for interacting with the Stock Options Liquid Hours Table.
    """
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrOptionTradingHours(IbkrBaseContracts):
    """!
    Class for interacting with the Stock Options Trading Hours Table.
    """
    insert_column_names = ["ibkr_contract_id", "begin_dt", "end_dt"]
    update_column_names = insert_column_names


class IbkrOptionNoHistory(IbkrBaseNoHistory):
    """!
    Class for interacting with Stock Options No History Table.
    """
    insert_column_names = ["ibkr_contract_id"]
    update_column_names = insert_column_names + ["last_updated"]
