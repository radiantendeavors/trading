"""!
@package pytrader.libs.accounts

Provides the Accounts Class for interacting with multiple accounts

@author Geoff S. Derber
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


@file pytrader/libs/accounts/__init__.py
Provides the Accounts Class for interacting with multiple accounts
"""
# System libraries

# 3rd Party libraries

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
class Accounts():
    """!
    Contains information about the available accounts.
    """

    def __init__(self, brokerclient):
        """!
        Initializes the Accounts class

        @param brokerclient - Provides the brokerclient

        @return None
        """
        logger.debug10("Begin Function")

        ## Brokerclient - Provides the Brokerclient
        self.brokerclient = brokerclient

        logger.debug10("End Function")
        return None

    def get_accounts(self):
        """!
        Gets a summary of the available accounts.

        @return None
        """
        logger.debug10("Begin Function")
        tags = ["AccountType", "TotalCashValue"]
        req_id = self.brokerclient.get_account_summary(tags=tags)
        accounts = self.brokerclient.get_data(req_id)

        logger.debug("Accounts: %s", accounts)
        logger.debug10("End Function")
        return None
