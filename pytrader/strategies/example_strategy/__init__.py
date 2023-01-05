"""!
@package pytrader.strategies.example_strategy

Provides an Example Strategy

@author Geoff S. Derber
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

@file pytrader/strategies/example_strategy/__init__.py

Provides an Example Strategy

"""
# System libraries

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.securities import security

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)

# ==================================================================================================
#
# Classes
#
# ==================================================================================================


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def run(brokerclient, securities):
    logger.debug10("Begin Function")
    logger.debug9("Running Example Strategy")

    investment = security.Security(security_type="etfs",
                                   ticker_symbol=securities[0],
                                   brokerclient=brokerclient)

    investment.set_contract()
    data = investment.get_broker_info()
    logger.debug("Data: %s", data)

    logger.debug10("End Function")
