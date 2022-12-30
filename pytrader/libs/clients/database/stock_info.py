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


@file pytrader/libs/clients/database/__init__.py
"""
from sqlalchemy import Column, Date, Integer, String, DateTime

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
class StockInfo(Base):
    __tablename__ = "etf_info"
    id = Column(Integer, Primary=True)
    ticker = Column(String, nullable=False)
    name = Column(String, nullable=True, default=None)
    sector = Column(String, nullable=True, default=None)
    industry = Column(String, nullable=True, default=None)
    country = Column(String, nullable=True, default=None)
    ibkr_symbol = Column(String, nullable=True, default=None)
    ibkr_contract_id = Column(String, nullable=True, default=None)
    ibkr_primary_exchange = Column(String, nullable=True, default=None)
    yahoo_symbol = Column(String, nullable=True, default=None)
    ipo_date = Column(DateTime, nullable=True, default=None)
    first_seen = Column(Date, nullable=True, default=None)
    last_seen = Column(Date, nullable=True, default=None)
    delisted_date = Column(Date, nullable=True, default=None)
