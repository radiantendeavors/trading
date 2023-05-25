"""!
@package pytrader.libs.clients.broker
Creates a basic interface for interacting with a broker

@file pytrader/libs/clients/broker/__init__.py

Creates a basic interface for interacting with a broker

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

"""
# System libraries
import threading

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients.broker.ibkr.tws.base import TwsBaseClient

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
class TwsApiThread(TwsBaseClient):

    def __init__(self, *args, **kwargs):
        self.queue = args[0]

        ##
        self.api_thread = threading.Thread(target=self.run, daemon=True)

        super().__init__(args, kwargs)
