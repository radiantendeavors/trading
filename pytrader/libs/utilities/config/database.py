"""!@package pytrader.libs.utilities.config.database

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


@file pytrader/libs/utilities/config/database.py
"""
import os

from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)
database_ports = {"sqlite": None, "mysql": "3306"}
home = os.path.expanduser("~") + "/"
config_dir = home + ".config/investing"


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class DatabaseConfig():
    """!
    Manages the configuration for the database.
    """

    database_type = "sqlite"
    database_driver = None
    database_username = None
    database_password = None
    database_host = "localhost"
    database_port = database_ports[database_type]
    database_path = config_dir
    database_name = "investing"
    database_url = None

    def read_config(self, *args, **kwargs):
        """!
        Parses the config file for dabatase related settings.
        """
        config = kwargs["config"]

        if "database_type" in config:
            self.database_type = config["database_type"]
            self.database_port = database_ports[self.database_type]

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

    def set_database_url(self, *args, **kwargs) -> str:
        """!
        Creates the database url based on the database settings.

        @return database_url: The url for the database.
        """
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
