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
# System libraries
from datetime import date, datetime, timedelta
from multiprocessing import Queue
from time import sleep
from typing import Optional

# 3rd Party libraries
from ibapi.contract import Contract as IbContract

# Application Libraries
from pytrader.libs.clients.database.mysql.ibkr.stk_opt_contracts import (
    IbkrStkOptContractDetails, IbkrStkOptContracts, IbkrStkOptHistoryBeginDate,
    IbkrStkOptInvalidContracts, IbkrStkOptLiquidHours, IbkrStkOptTradingHours)
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
class StkOptionContract(OptionContract):
    """!
    The AbstractBaseContract Class.
    """
    contract_table = IbkrStkOptContracts()
    contract_details_table = IbkrStkOptContractDetails()
    contract_liquid_hours_table = IbkrStkOptLiquidHours()
    contract_trading_hours_table = IbkrStkOptTradingHours()
    history_begin_date_table = IbkrStkOptHistoryBeginDate()
    invalid_contract_table = IbkrStkOptInvalidContracts()
