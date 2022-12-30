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
from sqlalchemy import BigInteger, Boolean, Column, Date, Float, Integer, String

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
class StockBarDailyRaw(Base):
    __tablename__ = "stock_bar_daily_raw"
    id = Column(Integer, Primary=True)
    ticker = Column(String)
    date = Column(Date)
    open = Column(Float, nullable=True, default=None)
    high = Column(Float, nullable=True, default=None)
    low = Column(Float, nullable=True, default=None)
    close = Column(Float, nullable=True, default=None)
    bid_open = Column(Float, nullable=True, default=None)
    bid_high = Column(Float, nullable=True, default=None)
    bid_low = Column(Float, nullable=True, default=None)
    bid_close = Column(Float, nullable=True, default=None)
    ask_open = Column(Float, nullable=True, default=None)
    ask_high = Column(Float, nullable=True, default=None)
    ask_low = Column(Float, nullable=True, default=None)
    ask_close = Column(Float, nullable=True, default=None)
    adjusted_open = Column(Float, nullable=True, default=None)
    adjusted_high = Column(Float, nullable=True, default=None)
    adjusted_low = Column(Float, nullable=True, default=None)
    adjusted_close = Column(Float, nullable=True, default=None)
    volume = Column(BigInteger, nullable=True, default=None)
    trade_count = Column(Integer, nullable=True, default=None)
    split = Column(Float, nullable=True, default=None)
    dividends = Column(Float, nullable=True, default=None)
    shares_outstanding = Column(BigInteger, nullable=True, default=None)
    shares_float = Column(BigInteger, nullable=True, default=None)
    outside_trading_hours = Column(Boolean)
    exchange = Column(String, nullable=True, default=None)
    data_source = Column(String)
    date_downloaded = Column(Date)
