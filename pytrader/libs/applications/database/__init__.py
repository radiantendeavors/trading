"""!@package pytrader.libs.applications.database

Manages the Database.

@author G S Derber
@version HEAD
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

@file pytrader/libs/applications/database/__init__.py

"""
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries

# 3rd Party libraries

# Application Libraries
from pytrader.libs.clients.database.sqlalchemy import Database
from pytrader.libs.clients.database.mysql import MySQLDatabase
from pytrader.libs.system import logging

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
class DatabaseManager():
    """!
    Manages the database.
    """
    database_status = None

    def initialize_database(self) -> None:
        """!
        Initializes the database."""
        database = Database()
        database.create_engine()
        database.create_session()
        database.create_tables()
        logger.debug("Initialization Complete!")

    def check_database_status(self) -> None:
        """!
        Checks and updates the database status.

        Changes database_status to one of:
          - NOTEXIST
          - REQUIRESUPGRADE
          - GOOD
        """
        database = MySQLDatabase()

        status = database.check_database_exists()

        if not status:
            self.database_status = "NOTEXIST"
        else:
            self.database_status = "GOOD"

        self.database_status = "NOTEXIST"

    def run(self) -> None:
        """!
        Runs the database process.

        @return None
        """
        self.check_database_status()

        match self.database_status:
            case "NOTEXIST":
                self.initialize_database()
            case "REQUIRESUPGRADE":
                self.upgrade_database()
            case "GOOD":
                logger.debug("Database is Good, doing nothing")
            case _:
                logger.error("Something didn't work!")

    def upgrade_database(self):
        """!
        Upgrades the database schema.
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")

# ==================================================================================================
#
# Functions
#
# ==================================================================================================
