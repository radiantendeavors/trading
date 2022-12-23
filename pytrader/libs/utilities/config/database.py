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

# System Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
# Enable Logging
# create logger
logger = logging.getLogger(__name__)
database_port = {"sqlite": None, "mysql": "3306"}
home = os.path.expanduser("~") + "/"
config_dir = home + ".config/investing"


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
        config = kwargs["config"]

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

    def set_database_url(self, *args, **kwargs):
        url = self.database_type

        if self.database_driver is not None:
            url = url + "+" + self.database_driver + "://"
        else:
            url = url + "://"

        if self.database_type == "sqlite":
            if self.database_name != "memory":
                url = url + "/" + self.database_path
                url = url + "/" + self.database_name
                url = url + ".db"
        else:
            if self.database_username is not None:
                if self.database_password is not None:
                    url = url + self.database_username + ":" + self.database_password
                else:
                    url = url + self.database_username

            url = url + "@" + self.database_host
            url = url + ":" + self.database_port
            url = url + "/" + self.database_name

        self.database_url = url
        return url
