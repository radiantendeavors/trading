"""!@package pytrader.libs.applications.strategy

The main user interface for the trading program.

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

@file pytrader/libs/applications/trader/__init__.py
"""
# System Libraries

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

"""
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class StrategyProcess():

    def start_strategy_process(self, strategy, brokerclient, process_queue,
                               securities_list, bar_sizes):
        logger.debug10("Begin Function")
        # strategy_process = multiprocessing.Process(
        #     target=strategy,
        #     args=(brokerclient, process_queue, securities_list, bar_sizes))
        # strategy_process.start()
        strategy(brokerclient, process_queue, securities_list, bar_sizes)
        logger.debug10("End Function")
        #return strategy_process
        return None
