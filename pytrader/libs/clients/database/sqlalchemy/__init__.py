"""!
@package pytrader.libs.clients.database.sqlalchemy

Defines the database schema, and creates the database tables.

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


@file pytrader/libs/clients/database/sqlalchemy/__init__.py
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from pytrader.libs.clients.database.sqlalchemy import ibkr
from pytrader.libs.system import logging
from pytrader.libs.utilities import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Database(ibkr.IbkrDBTables):
    """!
    Manages the various database tables.
    """

    db_session = None
    engine = None

    def __init__(self) -> None:
        """!
        Creates an instance of the Database Class.

        @return None
        """
        conf = config.Config()
        conf.read_config()
        self.database_url = conf.set_database_url()

    def create_session(self) -> None:
        """!
        Creates a database session.

        @return None
        """
        if self.engine is None:
            self.create_engine()

        self.db_session = Session(self.engine)
        # self.db_session.configure(bind=self.engine,
        #                           autoflush=False,
        #                           expire_on_commit=False)

    def create_engine(self) -> None:
        """!
        Creates the database engine.

        @return None
        """
        self.engine = create_engine(self.database_url)
