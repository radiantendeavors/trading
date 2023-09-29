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
from datetime import date, datetime, timedelta
from multiprocessing import Queue
from typing import Optional

# 3rd Party libraries
from ibapi.contract import Contract as IbContract
from ibapi.contract import ContractDetails

# Application Libraries
from pytrader.libs.contracts.base import BaseContract
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
class DatabaseContract(BaseContract):
    """!
    This class provides all methods required for interacting with the local database.
    """

    def __init__(self, ticker: Optional[str] = "", contract: Optional[IbContract] = None) -> None:
        """!
        Initializes an instance of the DatabesContract Class

        @param ticker:
        @param sec_type:
        @param contract:

        @return None
        """
        super().__init__(ticker, contract)
        self.id = 0
        self.columns = {}

    def query_contracts(self) -> list | tuple:
        criteria = {"symbol": [self.contract.symbol]}
        raw_results = self.contract_table.select(criteria=criteria)

        if raw_results:
            results = raw_results[0]
            logger.debug("Results: %s", results)
            self.id = results["id"]
            return results

        return False

    def query_history_begin_date(self) -> list | tuple:
        """!
        Query Contract History Begin Date.

        @return list or tuple:
        """
        criteria = {"ibkr_contract_id": [self.id]}
        return self.history_begin_date_table.select(criteria=criteria)

    def query_option_parameters(self) -> list | tuple:
        criteria = {"ibkr_contract_id": [self.id]}
        return self.option_parameters_table.select(criteria=criteria)

    def save_history_begin_date(self, history_begin_date) -> None:
        logger.debug("History Begin Date: %s", history_begin_date)
        begin_datetime = datetime.strptime(history_begin_date, "%Y%m%d  %H:%M:%S")
        self.history_begin_date_table.insert([self.id, begin_datetime])

    def save_option_parameters(self, option_parameters) -> None:
        logger.debug("Option Parameters: %s", option_parameters)
        expirations = ",".join(list(option_parameters["expirations"]))

        strikes = ",".join(list(map(str, option_parameters["strikes"])))
        insert_columns = [
            self.id, option_parameters["exchange"], option_parameters["multiplier"], expirations,
            strikes
        ]
        additional_parameters = {"exchange": [option_parameters["exchange"]]}
        self.option_parameters_table.insert(insert_columns, additional_parameters)
