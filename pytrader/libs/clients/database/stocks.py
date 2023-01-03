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
# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class StockInfo(Base):
    __tablename__ = "stock_info"
    id = Column(Integer, Primary=True)
    ticker = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey="company_info.id")
    primary_exchange = Column(Integer, ForeignKey="exchange_info.id")
    oldest_available = Column(DateTime)
    delisted_date = Column(Date, nullable=True, default=None)


class StockSectors(Base):
    __tablename__ = "stock_sectors"
    id = Column(Integer, Primary=True)
    sector = Column(String)


class StockIndustries(Base):
    __tablename__ = "stock_industries"
    id = Column(Integer, Primary=True)
    sector = Column(String)


class StockExchanges(Base):
    __tablename__ = "stock_exchanges"
    id = Column(Integer, Primary=True)
    stock_id = Column(Integer, ForeignKey="stock_info.id")
    exchange_id = Column(Integer, ForeignKey="exchange_info.id")
    begin_date = Column(Date)
    end_date = Column(Date)
