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

    def read_config(self, *args, **kwargs):
        if "database_type" in config:
            self.database_type = config["database_type"]
            self.database_port = database_port[self.database_type]

        if "database_driver" in config:
            self.database_driver = config["database_driver"]
        elif self.database_type == "sqlite":
            self.database_driver = "pysqlite"
        else:
            self.database_driver = None

        if "database_username" in config:
            self.database_username = config["database_username"]

        if "database_password" in config:
            self.database_password = config["database_password"]

        if "database_path" in config:
            self.database_path = config["database_path"]

        if "database_name" in config:
            self.database_name = config["database_name"]

        if "database_host" in config:
            self.database_host = config["database_host"]
