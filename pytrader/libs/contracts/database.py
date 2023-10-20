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
from datetime import datetime
from typing import Optional

from ibapi.contract import Contract as IbContract

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
        self.columns = {}

    def query_contracts(self, additional_criteria: Optional[dict] = None) -> list | tuple:
        """!
        Query Contracts Table

        @param additional_criteria: Contains additional query criteria.

        @return tuple: Query results
        """
        criteria = {"symbol": [self.contract.symbol]}

        if additional_criteria:
            criteria = criteria | additional_criteria

        logger.debug9("Criteria: %s", criteria)

        raw_results = self.contract_table.select(criteria=criteria)

        if raw_results:
            results = raw_results[0]
            logger.debug9("Results: %s", results)
            self.id = results["id"]
            return results

        return False

    def query_history_begin_date(self) -> list | tuple:
        """!
        Query Contract History Begin Date.

        @return list or tuple:
        """
        criteria = self._set_criteria()
        return self.history_begin_date_table.select(criteria=criteria)

    def query_option_parameters(self) -> list | tuple:
        """!
        Queries the Options Parameters table for information.

        @return list: The Query results.
        """
        criteria = self._set_criteria()
        return self.option_parameters_table.select(criteria=criteria)

    def save_history_begin_date(self, history_begin_date: str) -> None:
        """!
        Saves the history begin date to the database.

        @param history_begin_date: The first date with bar history available.

        @return None
        """
        if history_begin_date == "NoHistory" and self.no_history_table:
            self.no_history_table.insert([self.id])
        else:
            logger.debug("History Begin Date: %s", history_begin_date)
            begin_datetime = datetime.strptime(history_begin_date, "%Y%m%d  %H:%M:%S")
            self.history_begin_date_table.insert([self.id, begin_datetime])

    def save_option_parameters(self, option_parameters: dict) -> None:
        """!
        Saves Option Parameters to the database.

        @param option_parameters:

        @return None"""
        logger.debug("Option Parameters: %s", option_parameters)
        expirations = ",".join(list(option_parameters["expirations"]))

        strikes = ",".join(list(map(str, option_parameters["strikes"])))
        insert_columns = [
            self.id, option_parameters["exchange"], option_parameters["multiplier"], expirations,
            strikes
        ]
        additional_parameters = {"exchange": [option_parameters["exchange"]]}
        self.option_parameters_table.insert(insert_columns, additional_parameters)
