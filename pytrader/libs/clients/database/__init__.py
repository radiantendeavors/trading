"""!
@package pytrader.libs.clients.database

Defines the database schema, and creates the database tables.

@author Geoff S. Derber
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


@file pytrader/libs/clients/database/__init__.py
"""

# System Libraries

# 3rd Party Libraries
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.database import ibkr
from pytrader.libs.utilities import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logging logger
The base logger.

@var declarative_base Base
The Base Database

@var scoped_session DBSession
The Database Session
"""

logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Database(ibkr.IbkrDBTables):

    def __init__(self):
        conf = config.Config()
        conf.read_config()
        self.database_url = conf.set_database_url()
        self.engine = None

    def create_session(self):
        if self.engine is None:
            self.create_engine()

        self.db_session = Session(self.engine)
        # self.db_session.configure(bind=self.engine,
        #                           autoflush=False,
        #                           expire_on_commit=False)

        return self.db_session

    def create_engine(self):
        self.engine = create_engine(self.database_url)
