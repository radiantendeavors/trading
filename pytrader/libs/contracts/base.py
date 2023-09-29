"""!
@package pytrader.libs.contracts

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
from typing import Optional

# 3rd Party libraries
from ibapi.contract import Contract as IbContract

# Application Libraries
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
class BaseContract():
    """!
    The Base Contract Class
    """
    contract_table = None
    contract_details_table = None
    contract_liquid_hours_table = None
    contract_trading_hours_table = None
    history_begin_date_table = None
    option_parameters_table = None
    sec_type = None

    def __init__(self,
                 ticker: Optional[str] = "",
                 contract: Optional[IbContract] = None) -> None:
        """!
        Creates a contract
        """
        if contract:
            self.contract = contract
            self.sec_type = contract.secType

        else:
            self.contract = IbContract()
            self.contract.symbol = ticker

            # We keep the initial security type because that determines which database table to
            # query.  IBKR combines STK and ETF.  But we need to keep them separate.
            self.contract.secType = self._sanitize_security_type()

        self.details = None

    def _sanitize_security_type(self) -> str:
        """!
        Sanitizes the security type.  The format of the security type from webscraping the contract
        universe does not match the format required by the API.  This ensures that the security type
        is the correct type for the API.

        @param sec_type: Input Security Type

        @return sec_type: Sanitized Security Type
        """
        match self.sec_type.upper():
            case "FUTGRP":
                return "FUT"
            case _:
                logger.debug9("No changes to make for Security Type '%s'", self.sec_type)
                return self.sec_type
