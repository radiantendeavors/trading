"""!
@package pytrader.libs.clients.database.ibkr

Defines the database schema, and creates the database tables for Interactive Brokers related
information.

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


@file pytrader/libs/clients/database/ibkr.py
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
class IbkrEtfInfo(Base):
    __tablename__ = "z_ibkr_etf_info"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_id.id"), nullable=False)
    etf = relationship(EtfId)
    ticker_symbol = Column(String(6), nullable=False)
    contract_id = Column(Integer, nullable=False)
    primary_exchange = Column(String(32), nullable=False)
    exchange = Column(String(32), nullable=False)
    oldest_available = Column(DateTime)


class IbkrEtfBarDailyTrades(Base):
    __tablename__ = "z_ibkr_etf_bar_daily_trades"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"), nullable=False)
    etf = relationship(IbkrEtfInfo)
    date = Column(Date)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    count = Column(BigInteger, nullable=False)
    outside_trading_hours = Column(Boolean, nullable=False)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyBids(Base):
    __tablename__ = "z_ibkr_etf_bar_daily_bids"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    etf = relationship(IbkrEtfInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    outside_trading_hours = Column(Boolean)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyAsks(Base):
    __tablename__ = "z_ibkr_etf_bar_daily_asks"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    etf = relationship(IbkrEtfInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    outside_trading_hours = Column(Boolean)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyAdjusuted(Base):
    __tablename__ = "z_ibkr_etf_bar_daily_adjusted"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    etf = relationship(IbkrEtfInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    outside_trading_hours = Column(Boolean)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyHistoricalVolatility(Base):
    __tablename__ = "z_ibkr_etf_bar_daily_historical_volatility"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    etf = relationship(IbkrEtfInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyOptionImpliedVolatility(Base):
    __tablename__ = "z_ibkr_etf_bar_daily_option_implied_volatility"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    etf = relationship(IbkrEtfInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexInfo(Base):
    __tablename__ = "z_ibkr_index_info"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("index_info.id"))
    ticker_symbol = Column(String(6))
    contract_id = Column(Integer)
    exchange = Column(String(32))
    oldest_available = Column(DateTime)


class IbkrIndexBarDailyTrades(Base):
    __tablename__ = "z_ibkr_index_bar_daily_trades"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    index = relationship(IbkrIndexInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyBids(Base):
    __tablename__ = "z_ibkr_index_bar_daily_bids"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    index = relationship(IbkrIndexInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyAsks(Base):
    __tablename__ = "z_ibkr_index_bar_daily_asks"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    index = relationship(IbkrIndexInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyAdjusuted(Base):
    __tablename__ = "z_ibkr_index_bar_daily_adjusted"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    index = relationship(IbkrIndexInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyHistoricalVolatility(Base):
    __tablename__ = "z_ibkr_index_bar_daily_historical_volatility"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    index = relationship(IbkrIndexInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyOptionImpliedVolatility(Base):
    __tablename__ = "z_ibkr_index_bar_daily_option_implied_volatility"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    index = relationship(IbkrIndexInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockInfo(Base):
    __tablename__ = "z_ibkr_stock_info"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock_info.id"))
    ticker_symbol = Column(String(6))
    contract_id = Column(Integer)
    primary_exchange = Column(String(32))
    exchange = Column(String(32))
    oldest_available = Column(DateTime)


class IbkrStockBarDailyTrades(Base):
    __tablename__ = "z_ibkr_stock_bar_daily_trades"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    stock = relationship(IbkrStockInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyBids(Base):
    __tablename__ = "z_ibkr_stock_bar_daily_bids"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    stock = relationship(IbkrStockInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyAsks(Base):
    __tablename__ = "z_ibkr_stock_bar_daily_asks"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    stock = relationship(IbkrStockInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyAdjusuted(Base):
    __tablename__ = "z_ibkr_stock_bar_daily_adjusted"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    stock = relationship(IbkrStockInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyHistoricalVolatility(Base):
    __tablename__ = "z_ibkr_stock_bar_daily_historical_volatility"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    stock = relationship(IbkrStockInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyOptionImpliedVolatility(Base):
    __tablename__ = "z_ibkr_stock_bar_daily_option_implied_volatility"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    stock = relationship(IbkrStockInfo)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
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
