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
from pytrader.libs.clients.database.mysql.ibkr.option_contracts import (
    IbkrOptionContractDetails, IbkrOptionContracts, IbkrOptionHistoryBeginDate,
    IbkrOptionInvalidContracts, IbkrOptionLiquidHours, IbkrOptionNoHistory,
    IbkrOptionTradingHours)
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
class IbkrStkOptContracts(IbkrOptionContracts):
    """!
    Class for interacting with the Stock Options Contracts Table.
    """
    table_name = "z_ibkr_stk_opt_contracts"


class IbkrStkOptContractDetails(IbkrOptionContractDetails):
    """!
    Class for interacting with the Stock Options Contracts Details Table.
    """
    table_name = "z_ibkr_stk_opt_contract_details"


class IbkrStkOptInvalidContracts(IbkrOptionInvalidContracts):
    """!
    Class for interacting with the Stock Options Invalid Contracts Table.
    """
    table_name = "z_ibkr_stk_opt_invalid_contracts"


class IbkrStkOptHistoryBeginDate(IbkrOptionHistoryBeginDate):
    """!
    Class for interacting with the Stock Options History Begin Table.
    """
    table_name = "z_ibkr_stk_opt_history_begin_date"


class IbkrStkOptLiquidHours(IbkrOptionLiquidHours):
    """!
    Class for interacting with the Stock Options Liquid Hours Table.
    """
    table_name = "z_ibkr_stk_opt_liquid_hours"


class IbkrStkOptTradingHours(IbkrOptionTradingHours):
    """!
    Class for interacting with the Stock Options Trading Hours Table.
    """
    table_name = "z_ibkr_stk_opt_trading_hours"


class IbkrStkOptNoHistory(IbkrOptionNoHistory):
    """!
    Class for interacting with Stock Options No History Table.
    """
    table_name = "z_ibkr_stk_opt_no_history"
