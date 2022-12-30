"""!
@package pytrader.libs.security

Provides the broker client

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


@file security.py
"""
# System libraries

# 3rd Party libraries
from ibapi.contract import Contract

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Security():

    def __init__(self, *args, **kwargs):
        logger.debug10("Begin Function")
        logger.debug("Kwargs: %s", kwargs)
        if kwargs.get("ticker_symbol"):
            self.ticker_symbol = kwargs["ticker_symbol"]
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]

        logger.debug10("End Function")

    def set_contract(self,
                     ticker_symbol,
                     security_type,
                     primary_exchange=None,
                     exchange="SMART"):
        """!@fn set_contract

        @param security The ticker symbol for the contract
        @param security_type The type of security for the contract.  Can be one of: CASH, CRYPTO, STK, IND, CFD, FUT, CONTFUT, FUT+CONTFUT, OPT, FOP, BOND, FUND
        @param exchange
        @param currency
        """
        logger.debug10("Begin Function")
        contract = Contract()
        contract.symbol = ticker_symbol
        contract.secType = security_type
        contract.exchange = exchange
        contract.currency = "USD"
        logger.debug("Primary Exchange: %s", primary_exchange)
        if primary_exchange:
            contract.primaryExchange = primary_exchange

        logger.debug("Contract: %s", contract)

        logger.debug10("End Function")
        return contract
