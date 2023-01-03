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
from sqlalchemy import (BigInteger, Boolean, Column, Date, ForeignKey, Float,
                        Integer, String, Time)
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
class ExchangeInfo(Base):
    __tablename__ = "exchange_info"
    id = Column(Integer, Primary=True)
    name = Column(String)
    symbol = Column(String)


class ExchangeOperatingHours(Base):
    __tablename__ = "exchange_operating_hours"
    id = Column(Integer, Primary=True)
    exchange_id = Column(Integer, ForeignKey="exchange_info.id")
    date = Column(Date)
    premarket_open = Column(Time)
    market_open = Column(Time)
    market_close = Column(Time)
    afterhours_close = Column(Time)
    timezone_id = Column(Integer, ForeignKey="timezones")


class TimeZones(Base):
    __tablename__ = "timezones"
    id = Column(Integer, Primary=True)
    name = Column(String)
    code = Column(String)
