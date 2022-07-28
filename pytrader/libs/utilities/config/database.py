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
from pytrader.libs.utilities.config import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
# Enable Logging
# create logger
logger = logging.getLogger(__name__)
consolehandler = logging.ColorizingStreamHandler()


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class DatabaseConfig():

    def __init__(self):
        self.database_type = "sqlite"
        self.database_driver = None
        self.database_username = None
        self.database_password = None
        self.database_host = "localhost"
        self.database_port = database_port[self.database_type]
        self.database_path = config_dir
        self.database_name = "investing"
