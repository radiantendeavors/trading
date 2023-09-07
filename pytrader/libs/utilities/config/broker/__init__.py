"""!@package pytrader.libs.utilities.config.brokerconfig

Provides the config for the broker

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

@file pytrader/libs/utilities/config/brokerconfig.py
"""
# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# System Libraries

# System Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.utilities.config.broker import twsconfig

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
# Enable Logging
# create logger
logger = logging.getLogger(__name__)

BROKERS = {"twsapi": twsconfig.TwsConfig}


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BrokerConfig():

    def __init__(self, broker_id: str):
        self.config = BROKERS[broker_id]()

    def get_client_address(self):
        return self.config.get_client_address()

    def identify_clients(self):
        return self.config.identify_clients()

    def read_config(self, *args, **kwargs):
        config = kwargs["config"]

        if "brokerclient_address" in config:
            self.brokerclient_address = config["brokerclient_address"]

    def get_brokerclient_address(self):
        return self.brokerclient_address
