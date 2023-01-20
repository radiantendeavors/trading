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
class PolygonCommonStockInfo(Base):
    __tablename__ = "z_polygon_common_stock_info"
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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonCommonStockDetails(Base):
    __tablename__ = "z_polygon_common_stock_details"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, foreign_key=("z_polygon_common_stock_info.id"))
    stock = relationship(PolygonCommonStockInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonCommonStockDelisted(Base):
    __tablename__ = "z_polygon_common_stock_delisted"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, foreign_key=("z_polygon_common_stock_info.id"))
    stock = relationship(PolygonCommonStockInfo)
    delisted_utc = Column(DateTime)


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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonEtfDetails(Base):
    __tablename__ = "z_polygon_etf_details"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, foreign_key=("z_polygon_etf_info.id"))
    etf = relationship(PolygonEtfInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    composite_figi = Column(String(12))
    delisted_utc = Column(DateTime)
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonEtfDelisted(Base):
    __tablename__ = "z_polygon_etf_delisted"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, foreign_key=("z_polygon_etf_info.id"))
    etf = relationship(PolygonEtfInfo)
    delisted_utc = Column(DateTime)


class PolygonEtnInfo(Base):
    __tablename__ = "z_polygon_etn_info"
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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonEtnDetails(Base):
    __tablename__ = "z_polygon_etn_details"
    id = Column(Integer, primary_key=True)
    etn_id = Column(Integer, foreign_key=("z_polygon_etn_info.id"))
    etn = relationship(PolygonEtnInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    composite_figi = Column(String(12))
    delisted_utc = Column(DateTime)
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonEtnDelisted(Base):
    __tablename__ = "z_polygon_etn_delisted"
    id = Column(Integer, primary_key=True)
    etn_id = Column(Integer, foreign_key=("z_polygon_etn_info.id"))
    etn = relationship(PolygonEtnInfo)
    delisted_utc = Column(DateTime)


class PolygonEtsInfo(Base):
    __tablename__ = "z_polygon_ets_info"
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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonEtsDetails(Base):
    __tablename__ = "z_polygon_ets_details"
    id = Column(Integer, primary_key=True)
    ets_id = Column(Integer, foreign_key=("z_polygon_ets_info.id"))
    ets = relationship(PolygonEtsInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    composite_figi = Column(String(12))
    delisted_utc = Column(DateTime)
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonEtsDelisted(Base):
    __tablename__ = "z_polygon_ets_delisted"
    id = Column(Integer, primary_key=True)
    ets_id = Column(Integer, foreign_key=("z_polygon_ets_info.id"))
    ets = relationship(PolygonEtsInfo)
    delisted_utc = Column(DateTime)


class PolygonEtvInfo(Base):
    __tablename__ = "z_polygon_etv_info"
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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonEtvDetails(Base):
    __tablename__ = "z_polygon_etv_details"
    id = Column(Integer, primary_key=True)
    etv_id = Column(Integer, foreign_key=("z_polygon_etv_info.id"))
    etv = relationship(PolygonEtvInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    composite_figi = Column(String(12))
    delisted_utc = Column(DateTime)
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonEtvDelisted(Base):
    __tablename__ = "z_polygon_etv_delisted"
    id = Column(Integer, primary_key=True)
    etv_id = Column(Integer, foreign_key=("z_polygon_etv_info.id"))
    etv = relationship(PolygonEtvInfo)
    delisted_utc = Column(DateTime)


class PolygonIndexInfo(Base):
    __tablename__ = "z_polygon_index_info"
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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonIndexDetails(Base):
    __tablename__ = "z_polygon_index_details"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, foreign_key=("z_polygon_index_info.id"))
    stock = relationship(PolygonIndexInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonIndexDelisted(Base):
    __tablename__ = "z_polygon_index_delisted"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, foreign_key=("z_polygon_index_info.id"))
    stock = relationship(PolygonIndexInfo)
    delisted_utc = Column(DateTime)


class PolygonPreferredStockInfo(Base):
    __tablename__ = "z_polygon_preferred_stock_info"
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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonPreferredStockDetails(Base):
    __tablename__ = "z_polygon_preferred_stock_details"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer,
                      foreign_key=("z_polygon_preferred_stock_info.id"))
    stock = relationship(PolygonPreferredStockInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonPreferredStockDelisted(Base):
    __tablename__ = "z_polygon_preferred_stock_delisted"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer,
                      foreign_key=("z_polygon_preferred_stock_info.id"))
    stock = relationship(PolygonPreferredStockInfo)
    delisted_utc = Column(DateTime)


class PolygonWarrantInfo(Base):
    __tablename__ = "z_polygon_warrant_info"
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
    last_updated_utc = Column(DateTime)
    locale = Column(String(6))
    market = Column(String(6))
    primary_exchange = Column(String(6))
    share_class_figi = Column(String(12))


class PolygonWarrantDetails(Base):
    __tablename__ = "z_polygon_warrant_details"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, foreign_key=("z_polygon_warrant_info.id"))
    stock = relationship(PolygonWarrantInfo)
    address = Column(String(128))
    branding = Column(String(128))
    company_name = Column(String(64))
    description = Column(Text)
    homepage_url = Column(String(128))
    list_date = Column(DateTime)
    market_cap = Column(Float)
    phone_number = Column(String(12))
    share_class_shares_outstanding = Column(BigInteger)
    sic_code = Column(String(12))
    sic_description = Column(String(64))
    ticker_root = Column(String(6))
    weighted_shares_outstanding = Column(BigInteger)
    total_employees = Column(Integer)


class PolygonWarrantDelisted(Base):
    __tablename__ = "z_polygon_warrant_delisted"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, foreign_key=("z_polygon_warrant_info.id"))
    stock = relationship(PolygonWarrantInfo)
    delisted_utc = Column(DateTime)


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
