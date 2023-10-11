"""!
@package pytrader.libs.clients.mysql

Provides the mysql/mariadb database client

@author Geoff S. derber
@version HEAD
@date 2022
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


@file pytrader/libs/clients/mysql/__init__.py
"""
import pymysql

from pytrader.libs.system import logging
from pytrader.libs.utilities import config

# 3rd Party Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class MySQLDatabase():
    """!
    Class for interacting with a MySQL (or MariaDB) Database
    """

    def __init__(self) -> None:
        self.conf = config.Config()
        self.conf.read_config()

        self.host = self.conf.database_host
        self.user = self.conf.database_username
        self.password = self.conf.database_password
        self.database_name = self.conf.database_name

        try:
            self.mydb = pymysql.connect(host=self.host,
                                        user=self.user,
                                        password=self.password,
                                        database=self.database_name,
                                        cursorclass=pymysql.cursors.DictCursor)
            self.mycursor = self.mydb.cursor()
        except pymysql.Error as msg:
            logger.error("Connection failed: %s", msg)

    def check_database_exists(self) -> bool:
        """!
        Checks if the database exist.

        @return bool:
             - True if the database exists
             - False if the database does not exist
        """
        logger.debug("Begin Function")
        sql = "SHOW DATABASES LIKE '" + self.conf.database_name + "'"
        logger.debug("SQL: %s", sql)
        try:
            row = self.mycursor.execute(sql)
            logger.debug("Row: %s", row)
            return True
        except pymysql.Error as msg:
            logger.error("Check Database's Existance Failed: %s", msg)
            return False

    def check_table_exists(self, table_name: str) -> bool:
        """!
        Checks if a given table exists

        @param table_name: The table being verified for existence.

        @return bool:
             - True if the database exists
             - False if the database does not exist
        """
        logger.debug("Begin Function")
        sql = "SELECT * FROM information_schema.tables Where table_name = '" + table_name + "'"
        logger.debug("SQL: %s", sql)
        try:
            row = self.mycursor.execute(sql)
            logger.debug("Row: %s", row)
            return True
        except pymysql.Error as msg:
            logger.error("Check Table's Existance Failed: %s", msg)
            return False

    def substitute_list(self, values: list) -> str:
        """!
        Turns a list of values into a string for mysql string substitution.
        """
        return ", ".join(list(map(lambda x: '%s', values)))
