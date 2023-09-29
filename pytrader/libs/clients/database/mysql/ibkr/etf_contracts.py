"""!
@package pytrader.libs.clients.mysql.etf_info

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
from typing import Optional

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
class IbkrEtfContracts(IbkrBaseContracts):
    table_name = "z_ibkr_etf_contracts"
    insert_column_names = [
        "contract_id", "ticker_symbol", "security_type", "exchange", "currency", "local_symbol",
        "primary_exchange", "trading_class"
    ]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrEtfContractDetails(IbkrBaseContracts):
    table_name = "z_ibkr_etf_contract_details"
    insert_column_names = [
        "ibkr_contract_id", "market_name", "min_tick", "price_magnifier", "valid_exchanges",
        "long_name", "timezone_id", "stock_type", "aggregated_group"
    ]
    update_column_names = insert_column_names


class IbkrEtfExchanges(IbkrBaseContracts):
    table_name = "z_ibkr_etf_exchanges"
    insert_column_names = ["ibkr_contract_id", "exchange"]
    update_column_names = insert_column_names


class IbkrEtfHistoryBeginDate(IbkrBaseContracts):
    table_name = "z_ibkr_etf_history_begin_date"
    insert_column_names = ["ibkr_contract_id", "oldest_datetime"]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrEtfLiquidHours(IbkrBaseContracts):
    table_name = "z_ibkr_etf_liquid_hours"
    insert_column_names = ["ibkr_contract_id", "liquid_hours"]
    update_column_names = insert_column_names


class IbkrEtfOrderTypes(IbkrBaseContracts):
    table_name = "z_ibkr_etf_order_types"
    insert_column_names = ["ibkr_contract_id", "order_type"]
    update_column_names = insert_column_names


class IbkrEtfOptParams(IbkrBaseContracts):
    table_name = "z_ibkr_etf_option_parameters"
    insert_column_names = ["ibkr_contract_id", "exchange", "multiplier", "expirations", "strikes"]
    update_column_names = insert_column_names + ["last_updated"]


class IbkrEtfTradingHours(IbkrBaseContracts):
    table_name = "z_ibkr_etf_liquid_hours"
    insert_column_names = ["ibkr_contract_id", "trading_hours"]
    update_column_names = insert_column_names
