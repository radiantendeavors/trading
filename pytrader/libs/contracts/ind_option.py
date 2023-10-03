"""!
@package pytrader.libs.contracts.abstractbase

Provides the Base Class for Contracts

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


@file pytrader/libs/contracts/__init__.py

Provides the Base Class for Contracts
"""
from pytrader.libs.clients.database.mysql.ibkr.ind_opt_contracts import (
    IbkrIndOptContractDetails, IbkrIndOptContracts, IbkrIndOptHistoryBeginDate,
    IbkrIndOptInvalidContracts, IbkrIndOptLiquidHours, IbkrIndOptTradingHours)
from pytrader.libs.contracts.option import OptionContract
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
class IndOptionContract(OptionContract):
    """!
    The Index Option Contract Class.
    """
    contract_table = IbkrIndOptContracts()
    contract_details_table = IbkrIndOptContractDetails()
    contract_liquid_hours_table = IbkrIndOptLiquidHours()
    contract_trading_hours_table = IbkrIndOptTradingHours()
    history_begin_date_table = IbkrIndOptHistoryBeginDate()
    invalid_contract_table = IbkrIndOptInvalidContracts()
