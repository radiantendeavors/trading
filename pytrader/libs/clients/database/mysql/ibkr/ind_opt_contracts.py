"""!
@package pytrader.libs.clients.database.mysql.ibkr.ind_opt_contracts

Provides classes for interacting with index option related tables.

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
class IbkrIndOptContracts(IbkrOptionContracts):
    """!
    Class for interacting with the Index Options Contracts Table.
    """
    table_name = "z_ibkr_ind_opt_contracts"


class IbkrIndOptContractDetails(IbkrOptionContractDetails):
    """!
    Class for interacting with the Index Options Contracts Details Table.
    """
    table_name = "z_ibkr_ind_opt_contract_details"


class IbkrIndOptInvalidContracts(IbkrOptionInvalidContracts):
    """!
    Class for interacting with the Index Options Invalid Contracts Table.
    """
    table_name = "z_ibkr_ind_opt_invalid_contracts"


class IbkrIndOptHistoryBeginDate(IbkrOptionHistoryBeginDate):
    """!
    Class for interacting with the Index Options History Begin Table.
    """
    table_name = "z_ibkr_ind_opt_history_begin_date"


class IbkrIndOptLiquidHours(IbkrOptionLiquidHours):
    """!
    Class for interacting with the Index Options Liquid Hours Table.
    """
    table_name = "z_ibkr_ind_opt_liquid_hours"


class IbkrIndOptTradingHours(IbkrOptionTradingHours):
    """!
    Class for interacting with the Index Options Trading Hours Table.
    """
    table_name = "z_ibkr_ind_opt_trading_hours"


class IbkrIndOptNoHistory(IbkrOptionNoHistory):
    """!
    Class for interacting with Index Options No History Table.
    """
    table_name = "z_ibkr_ind_opt_no_history"
