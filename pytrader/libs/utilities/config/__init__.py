#! /usr/bin/env python3
# ==================================================================================================
#
#
# Config:
#
#    Sets program configuration
#
# ==================================================================================================

# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# System Libraries
import os
import yaml

# System Overrides
from pytrader.libs.system import logging
# Other Application Libraries

from pytrader.libs.utilities.config import (logconfig, brokerconfig, database,
                                            polygon, redditconfig)
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

home = os.path.expanduser("~") + "/"
config_dir = home + ".config/investing"
config_file = config_dir + "/config.yaml"
config_stream = open(config_file)
config = yaml.safe_load(config_stream)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Config(brokerconfig.BrokerConfig, database.DatabaseConfig,
             logconfig.LogConfig, polygon.PolygonConfig,
             redditconfig.RedditConfig):

    def __init__(self, *args, **kwargs):
        self.nasdaq_client_key = None
        self.nasdaq_client_secret = None
        super().__init__()
        return None

    def read_config(self, *args, **kwargs):
        logconfig.LogConfig.read_config(self, config=config)
        database.DatabaseConfig.read_config(self, config=config)
        brokerconfig.BrokerConfig.read_config(self, config=config)
        polygon.PolygonConfig.read_config(self, config=config)
