"""!
@package pytrader.libs.clients.database

Defines the database schema, and creates the database tables.

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


@file pytrader/libs/clients/database/__init__.py
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


# ==================================================================================================
#
# Merged Info Tables
#
# ==================================================================================================
class ExchangeInfo(Base):
    __tablename__ = "exchange_info"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    symbol = Column(String(8))


class CompanyId(Base):
    __tablename__ = "company_id"
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(64))


class EtfId(Base):
    __tablename__ = "etf_id"
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(64))


class IndexId(Base):
    __tablename__ = "index_id"
    id = Column(Integer, primary_key=True)
    unique_id = Column(String(64))


class EtfInfo(Base):
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_id.id"))
    etf = relationship(EtfId)
    ticker_symbol = Column(String(6))
    name = Column(String(64))


class StockInfo(Base):
    __tablename__ = "stock_info"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    company = relationship(CompanyId)
    primary_exchange_id = Column(Integer, ForeignKey("exchange_info.id"))
    primary_exchange = relationship(ExchangeInfo)


class AddressCountry(Base):
    __tablename__ = "address_country"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code2 = Column(String(length=2))
    code3 = Column(String(length=3))


class AddressState(Base):
    __tablename__ = "address_state"
    id = Column(Integer, primary_key=True)
    state = Column(String)
    code = Column(String)
    country_id = Column(Integer, ForeignKey("address_country.id"))
    country = relationship(AddressCountry)


class AddressCity(Base):
    __tablename__ = "address_city"
    id = Column(Integer, primary_key=True)
    city = Column(String)
    state_id = Column(Integer, ForeignKey("address_state.id"))
    state = relationship(AddressState)


class AddressStreet(Base):
    __tablename__ = "address_street"
    id = Column(Integer, primary_key=True)
    address1 = Column(String)
    address2 = Column(String)
    zip = Column(Integer)
    city_id = Column(Integer, ForeignKey("address_city.id"))
    city = relationship(AddressCity)


class StockSectors(Base):
    __tablename__ = "stock_sectors"
    id = Column(Integer, primary_key=True)
    sector = Column(String(32))


class StockIndustries(Base):
    __tablename__ = "stock_industries"
    id = Column(Integer, primary_key=True)
    sector = Column(String(32))


class AggregateEtfBarDaily(Base):
    __tablename__ = "aggregate_etf_bar_daily"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6), nullable=False)
    date = Column(Date, nullable=False)
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
    outside_trading_hours = Column(Boolean)


# class AggregateIndexBarDaily(Base):
#     __tablename__ = "index_bar_daily_raw"
#     id = Column(Integer, primary_key=True)
#     ticker = Column(String, nullable=False)
#     open = Column(Float, nullable=True, default=None)
#     high = Column(Float, nullable=True, default=None)
#     low = Column(Float, nullable=True, default=None)
#     close = Column(Float, nullable=True, default=None)
#     adjusted_close = Column(Float, nullable=True, default=None)
#     volume = Column(Float, nullable=True, default=None)
#     data_source = Column(String)
#     date_downloaded = Column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)


class AggregateStockBarDaily(Base):
    __tablename__ = "aggregate_stock_bar_daily"
    id = Column(Integer, primary_key=True)
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
    outside_trading_hours = Column(Boolean)


class CompanyAddress(Base):
    __tablename__ = "company_address"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    company = relationship(CompanyId)
    address_id = Column(Integer, ForeignKey("address_street.id"))
    address = relationship(AddressStreet)
    beginning_date = Column(Date)
    end_date = Column(Date)


class CompanyName(Base):
    __tablename__ = "company_name"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    company_id = Column(Integer, ForeignKey("company_id.id"))
    company = relationship(CompanyId)
    begin_date = Column(Date)
    end_date = Column(Date)


class CompanySector(Base):
    __tablename__ = "company_sector"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    sector_id = Column(Integer, ForeignKey("stock_sectors.id"))
    company = relationship(CompanyId)
    sector = relationship(StockSectors)


class CompanyIndustry(Base):
    __tablename__ = "company_industry"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    industry_id = Column(Integer, ForeignKey("stock_industries.id"))
    company = relationship(CompanyId)
    sector = relationship(StockSectors)


class CompanyStockListing(Base):
    __tablename__ = "company_stock_listing"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    company = relationship(CompanyId)
    ipo_date = Column(Date)


class CompanyStockDelisting(Base):
    __tablename__ = "company_stock_delisting"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    company = relationship(CompanyId)
    delisting_date = Column(Date)


class EtfListing(Base):
    __tablename__ = "etf_listing"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_id.id"))
    etf = relationship(EtfId)


class EtfExchanges(Base):
    __tablename__ = "etf_exchanges"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_id.id"))
    etf = relationship(EtfId)
    exchange_id = Column(Integer, ForeignKey("exchange_info.id"))
    exchange = relationship(ExchangeInfo)
    begin_date = Column(Date)
    end_date = Column(Date)


class ExchangeOperatingHours(Base):
    __tablename__ = "exchange_operating_hours"
    id = Column(Integer, primary_key=True)
    exchange_id = Column(Integer, ForeignKey("exchange_info.id"))
    date = Column(Date)
    premarket_open = Column(Time)
    market_open = Column(Time)
    market_close = Column(Time)
    afterhours_close = Column(Time)
    timezone_id = Column(Integer, ForeignKey("timezones"))


class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(64))
    value = Column(String(64))


class StockExchanges(Base):
    __tablename__ = "stock_exchanges"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_id.id"))
    company = relationship(CompanyId)
    exchange_id = Column(Integer, ForeignKey("exchange_info.id"))
    exchange = relationship(ExchangeInfo)
    begin_date = Column(Date)
    end_date = Column(Date)


class TimeZones(Base):
    __tablename__ = "timezones"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    code = Column(String(8))


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
