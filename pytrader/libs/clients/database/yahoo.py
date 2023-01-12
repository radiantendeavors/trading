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
from pytrader.libs.clients.database import (EtfInfo)
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
class YahooEtfInfo(Base):
    __tablename__ = "yahoo_etf_info"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_info.id"))
    etf = relationship(EtfInfo)
    ticker_symbol = Column(String(8))


class YahooEtfBarDaily(Base):
    __tablename__ = "yahoo_etf_bar_daily"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_info.id"))
    etf = relationship(EtfInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class YahooEtfDividends(Base):
    __tablename__ = "yahoo_etf_dividends"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_info.id"))
    date = Column(Date)
    dividend = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class YahooEtfSplits(Base):
    __tablename__ = "yahoo_etf_splits"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_info.id"))
    date = Column(Date, nullable=False)
    split = Column(Float, nullable=True, default=None)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class YahooIndexInfo(Base):
    __tablename__ = "yahoo_index_info"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("index_info.id"))
    ticker_symbol = Column(String(6))
    first_seen = Column(Date)
    last_seen = Column(Date)


class YahooStockInfo(Base):
    __tablename__ = "yahoo_stock_info"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    ticker = Column(String(8), nullable=False)
    oldest_available = Column(DateTime)
    delisted_date = Column(Date, nullable=True, default=None)
    first_seen = Column(Date)
    last_seen = Column(Date)


class YahooStockBarDaily(Base):
    __tablename__ = "yahoo_stock_bar_daily"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class YahooStockDividends(Base):
    __tablename__ = "yahoo_stock_dividends"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    date = Column(Date)
    dividend = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class YahooStockSplits(Base):
    __tablename__ = "yahoo_stock_splits"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    date = Column(Date)
    split = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def init_sqlalchemy():
    logger.debug("Begin Function")
    global engine
    conf = config.Config()
    conf.read_config()
    database_url = conf.set_database_url()
    engine = create_engine(database_url)
    DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    logger.debug("End Function")
