"""!@package pytrader.libs.utilities.config

Reads the config files.

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


@file pytrader/libs/utilities/config/__init__.py
"""
import os

import yaml

from pytrader.libs.system import logging
from pytrader.libs.utilities.config import (broker, database, logconfig,
                                            polygon, redditconfig)

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)

home = os.path.expanduser("~") + "/"
config_dir = home + ".config/investing"
config_file = config_dir + "/config.yaml"

with open(config_file, 'r', encoding='utf-8') as config_stream:
    config = yaml.safe_load(config_stream)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Config(broker.BrokerConfig, database.DatabaseConfig, logconfig.LogConfig,
             polygon.PolygonConfig, redditconfig.RedditConfig):
    """!
    Class for reading the config file.
    """

    nasdaq_client_key = None
    nasdaq_client_secret = None

    def __init__(self, *args, **kwargs) -> None:
        """!
        Initializes the Config Class.

        @param *args:
        @param **kwargs:

        @return None
        """
        super().__init__("twsapi")

    def read_config(self, *args, **kwargs) -> None:
        """!
        Reads the config files

        @param *args:
        @param **kwargs:

        @return None
        """
        broker.BrokerConfig.read_config(self, config=config)
        logconfig.LogConfig.read_config(self, config=config)
        database.DatabaseConfig.read_config(self, config=config)
        polygon.PolygonConfig.read_config(self, config=config)
