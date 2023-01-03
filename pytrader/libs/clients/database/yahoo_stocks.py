"""!
@package pytrader.libs.clients.database

Provides the database client

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


@file pytrader/libs/clients/database/etf_bar_daily_raw.py
"""
from sqlalchemy import (BigInteger, Boolean, Column, Date, Float, Integer,
                        String, ForeignKey, DateTime)
from sqlalchemy.orm import relationship

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.database import Base

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
class YahooEtfInfo(Base):
    __tablename__ = "yahoo_etf_info"
    id = Column(Integer, Primary=True)
    etf_id = Column(Integer, ForeignKey="etf_info.id")
    oldest_available = Column(DateTime)
    delisted_date = Column(Date, nullable=True, default=None)
    first_seen = Column(Date)
    last_seen = Column(Date)


class YahooEtfBarDaily(Base):
    __tablename__ = "yahoo_etf_bar_daily"
    id = Column(Integer, Primary=True)
    etf_id = Column(Integer, ForeignKey="etf_info.id")
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date)


class YahooEtfDividends(Base):
    __tablename__ = "yahoo_etf_dividends"
    id = Column(Integer, Primary=True)
    etf_id = Column(Integer, ForeignKey="etf_info.id")
    date = Column(Date)
    dividend = Column(Float)
    date_downloaded = Column(Date)


class YahooEtfDividends(Base):
    __tablename__ = "yahoo_etf_dividends"
    id = Column(Integer, Primary=True)
    etf_id = Column(Integer, ForeignKey="etf_info.id")
    date = Column(Date, nullable=False)
    split = Column(Float, nullable=True, default=None)
    date_downloaded = Column(Date)


class YahooStockInfo(Base):
    __tablename__ = "yahoo_stock_info"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    ticker = Column(String, nullable=False)
    oldest_available = Column(DateTime)
    delisted_date = Column(Date, nullable=True, default=None)
    first_seen = Column(Date)
    last_seen = Column(Date)


class YahooStockBarDaily(Base):
    __tablename__ = "yahoo_stock_bar_daily"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date)


class YahooStockDividends(Base):
    __tablename__ = "yahoo_stock_dividends"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    date = Column(Date)
    dividend = Column(Float)
    date_downloaded = Column(Date)


class YahooStockSplits(Base):
    __tablename__ = "yahoo_stock_splits"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    date = Column(Date)
    split = Column(Float)
    date_downloaded = Column(Date)
