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
from pytrader import git_branch
from pytrader.libs.system import logging
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
        self.brokerclient_account = None

    def get_client_address(self):
        return self.config.get_client_address()

    def identify_clients(self):
        return self.config.identify_clients()

    def read_config(self, *args, **kwargs):
        config = kwargs["config"]

        if git_branch == "main":
            if "ibkr_real_account" in config:
                self.brokerclient_account = config["ibkr_real_account"]
        else:
            if "ibkr_demo_account" in config:
                self.brokerclient_account = config["ibkr_demo_account"]