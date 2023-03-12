"""!
@package pytrader.libs.clients.database.yahoo

Defines the database schema, and creates the database tables for Yahoo related information.

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


@file pytrader/libs/clients/database/yahoo.py
"""

# System Libraries
from sqlalchemy import (BigInteger, Boolean, Column, Date, DateTime,
                        FetchedValue, Float, ForeignKey, Integer, String, Time)
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
"""!
@var logging logger
The base logger.

@var declarative_base Base
The Base Database

@var scoped_session DBSession
The Database Session
"""

logger = logging.getLogger(__name__)
Base = declarative_base()
DBSession = scoped_session(sessionmaker())


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class NasdaqEtfInfo(Base):
    __tablename__ = "nasdaq_etf_info"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    company_name = Column(String(64))
    first_seen = Column(Date,
                        server_default=func.current_timestamp(),
                        nullable=False)
    last_seen = Column(Date, nullable=False)


class NasdaqStockInfo(Base):
    __tablename__ = "nasdaq_stock_info"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    company_name = Column(String(64))
    country = Column(String(64))
    industry = Column(String(64))
    sector = Column(String(64))
    first_seen = Column(Date,
                        server_default=func.current_timestamp(),
                        nullable=False)
    last_seen = Column(Date, nullable=False)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def init_sqlalchemy(database_url):
    logger.debug("Begin Function")
    global engine
    engine = create_engine(database_url)
    DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    logger.debug("End Function")
