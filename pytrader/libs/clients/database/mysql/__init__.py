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
# System Libraries
import pymysql

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging
# Other Application Libraries
from pytrader.libs.utilities import config

# 3rd Party Libraries

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


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class MySQLDatabase():
    """!Class MySQLDatabase

    """

    def __init__(self, *args, **kwargs):
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
            return None
        except pymysql.Error as e:
            logger.error("Connection failed: %s", e)

    def check_database_exists(self):
        logger.debug("Begin Function")
        sql = "SHOW DATABASES LIKE '" + self.conf.database_name + "'"
        logger.debug("SQL: %s", sql)
        try:
            row = self.mycursor.execute(sql)
            logger.debug("Row: %s", row)
            return True
        except pymysql.Error as e:
            logger.error("Check Database's Existance Failed: %s", e)
            return False

    def check_table_exists(self, table_name):
        logger.debug("Begin Function")
        sql = "SELECT * FROM information_schema.tables Where table_name = '" + table_name + "'"
        logger.debug("SQL: %s", sql)
        try:
            row = self.mycursor.execute(sql)
            logger.debug("Row: %s", row)
        except pymysql.Error as e:
            logger.error("Check Table's Existance Failed: %s", e)

    def create_database(self, table_name: str):
        sql = "CREATE TABLE IF NOT EXISTS " + table_name
        logger.debug("Create Database SQL: %s", sql)

        try:
            self.mycursor.execute(sql)
        except pymysql.Error as e:
            logger.error("Connection Error: %s", e)

    def substitute_list(self, values: list) -> str:
        return ", ".join(list(map(lambda x: '%s', values)))
