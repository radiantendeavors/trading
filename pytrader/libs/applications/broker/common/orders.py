"""!
@package pytrader.libs.applications.broker.common.orders

Manages orders within the Broker Application.

@author G. S. Derber
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


@file pytrader/libs/applications/broker/common/orders.py
"""
# Standard libraries

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import orders

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Order(orders.BaseOrder):
    """!
    Manages orders within the Broker application.
    """
    pass
