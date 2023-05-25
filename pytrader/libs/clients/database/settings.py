"""!
@package pytrader.libs.clients.database.settings

Defines the database schema, and creates the database tables managing settings.

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


@file pytrader/libs/clients/database/settings.py
"""

# System Libraries
from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime,
                        FetchedValue, Float, ForeignKey, Integer, String, Text,
                        Time)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.utilities import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)

## The Base Database
Base = declarative_base()

## The Database Session
DBSession = scoped_session(sessionmaker())


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Settings(Base):
    __tablename__ = "Settings"
    id = Column(Integer, primary_key=True)
    setting = Column(String(256))
    value = Column(String(256))
