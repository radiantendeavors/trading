"""!@package pytrader.libs.utilities.config.brokerconfig

Parse the config settings for the broker.

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


@file pytrader/libs/utilities/config/brokerconfig.py
"""
from pytrader import CLIENT_ID, git_branch
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
# Enable Logging
# create logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BrokerConfig():

    def __init__(self, *args, **kwargs):
        self.brokerclient_address = "127.0.0.1"
        self.brokerclient_id = CLIENT_ID
        self.brokerclient_account = None

    def read_config(self, *args, **kwargs):
        config = kwargs["config"]

        if "brokerclient_address" in config:
            self.brokerclient_address = config["brokerclient_address"]

        if git_branch == "main":
            if "ibkr_real_account" in config:
                self.brokerclient_account = config["ibkr_real_account"]
        else:
            if "ibkr_demo_account" in config:
                self.brokerclient_address = config["ibkr_demo_account"]

    def get_brokerclient_address(self):
        return self.brokerclient_address
