"""!
@package pytrader.libs.clients.database.polygon

Defines the database schema, and creates the database tables for Polygon.io related information.

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


@file pytrader/libs/clients/database/polygon.py
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
class PolygonEtfInfo(Base):
    __tablename__ = "z_polygon_etf_info"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    company_name = Column(String(64))
    active = Column(Boolean)
    cik = Column(Integer)
    composite_figi = Column(String(12))
    currency_name = Column(String(6))
    currency_symbol = Column(String(6))
    base_currency_symbol = Column(String(6))
    base_currency_name = Column(String(6))
    delisted_utc = Column(DateTime)
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonEtfDetails(Base):
    __tablename__ = "z_polygon_etf_details"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    active = Column(Boolean)
    address = Column(String(128))
    base_currency_name = Column(String(6))
    base_currency_symbol = Column(String(6))
    branding = Column(String(128))
    cik = Column(Integer)
    company_name = Column(String(64))
    composite_figi = Column(String(12))
    currency_name = Column(String(6))
    currency_symbol = Column(String(6))
    delisted_utc = Column(DateTime)
    description = Column(Text)
    homepage_url = Column(String(128))
    last_updated_utc = Column(DateTime)
    list_date = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    market_cap = Column(Float)
    phone_number = Column(String(12))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonStockInfo(Base):
    __tablename__ = "z_polygon_stock_info"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    company_name = Column(String(64))
    active = Column(Boolean)
    cik = Column(Integer)
    composite_figi = Column(String(12))
    currency_name = Column(String(6))
    currency_symbol = Column(String(6))
    base_currency_symbol = Column(String(6))
    base_currency_name = Column(String(6))
    delisted_utc = Column(DateTime)
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonStockDetails(Base):
    __tablename__ = "z_polygon_stock_details"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    active = Column(Boolean)
    address = Column(String(128))
    base_currency_name = Column(String(6))
    base_currency_symbol = Column(String(6))
    branding = Column(String(128))
    cik = Column(Integer)
    company_name = Column(String(64))
    composite_figi = Column(String(12))
    currency_name = Column(String(6))
    currency_symbol = Column(String(6))
    delisted_utc = Column(DateTime)
    description = Column(Text)
    homepage_url = Column(String(128))
    last_updated_utc = Column(DateTime)
    list_date = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    market_cap = Column(Float)
    phone_number = Column(String(12))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


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
