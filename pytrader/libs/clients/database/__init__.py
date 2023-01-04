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
@var logger
The base logger.

@var Base

@var DBSession
"""
logger = logging.getLogger(__name__)
Base = declarative_base()
DBSession = scoped_session(sessionmaker())


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
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
    company_id = Column(Integer, ForeignKey("company_info.id"))
    address_id = Column(Integer, ForeignKey("address_street.id"))
    beginning_date = Column(Date)
    end_date = Column(Date)


class CompanyInfo(Base):
    __tablename__ = "company_info"
    id = Column(Integer, primary_key=True)
    cik = Column(Integer)
    begin_date = Column(Date)
    end_date = Column(Date)


class CompanyName(Base):
    __tablename__ = "company_name"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    company_id = Column(Integer, ForeignKey("company_info.id"))
    company = relationship(CompanyInfo)
    begin_date = Column(Date)
    end_date = Column(Date)


class CompanySector(Base):
    __tablename__ = "company_sector"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_info.id"))
    sector_id = Column(Integer, ForeignKey("stock_sectors.id"))
    company = relationship(CompanyInfo)
    sector = relationship(StockSectors)


class CompanyIndustry(Base):
    __tablename__ = "company_industry"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_info.id"))
    industry_id = Column(Integer, ForeignKey("stock_industries.id"))
    company = relationship(CompanyInfo)
    sector = relationship(StockSectors)


class CompanyStockListing(Base):
    __tablename__ = "company_stock_listing"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_info.id"))
    company = relationship(CompanyInfo)
    ipo_date = Column(Date)


class CompanyStockDelisting(Base):
    __tablename__ = "company_stock_delisting"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_info.id"))
    company = relationship(CompanyInfo)
    delisting_date = Column(Date)


class EtfInfo(Base):
    __tablename__ = "etf_info"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    name = Column(String, nullable=True, default=None)
    yahoo_symbol = Column(String, nullable=True, default=None)
    ipo_date = Column(DateTime, nullable=True, default=None)
    first_seen = Column(Date, nullable=True, default=None)
    last_seen = Column(Date, nullable=True, default=None)
    delisted_date = Column(Date, nullable=True, default=None)


class ExchangeInfo(Base):
    __tablename__ = "exchange_info"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    symbol = Column(String(8))


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


class IbkrEtfInfo(Base):
    __tablename__ = "ibkr_etf_info"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("etf_info.id"), nullable=False)
    ticker_symbol = Column(String(6), nullable=False)
    contract_id = Column(Integer, nullable=False)
    primary_exchange = Column(String(32), nullable=False)
    exchange = Column(String(32), nullable=False)
    oldest_available = Column(DateTime)
    etf = relationship(EtfInfo)


class IbkrEtfBarDailyTrades(Base):
    __tablename__ = "ibkr_etf_bar_daily_trades"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"), nullable=False)
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
    etf = relationship(EtfInfo)


class IbkrEtfBarDailyBids(Base):
    __tablename__ = "ibkr_etf_bar_daily_bids"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    outside_trading_hours = Column(Boolean)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyAsks(Base):
    __tablename__ = "ibkr_etf_bar_daily_asks"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    outside_trading_hours = Column(Boolean)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyAdjusuted(Base):
    __tablename__ = "ibkr_etf_bar_daily_adjusted"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
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
    __tablename__ = "ibkr_etf_bar_daily_historical_volatility"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrEtfBarDailyOptionImpliedVolatility(Base):
    __tablename__ = "ibkr_etf_bar_daily_option_implied_volatility"
    id = Column(Integer, primary_key=True)
    etf_id = Column(Integer, ForeignKey("ibkr_etf_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexInfo(Base):
    __tablename__ = "ibkr_index_info"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("index_info.id"))
    ticker_symbol = Column(String(6))
    contract_id = Column(Integer)
    exchange = Column(String(32))
    oldest_available = Column(DateTime)


class IbkrIndexBarDailyTrades(Base):
    __tablename__ = "ibkr_index_bar_daily_trades"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyBids(Base):
    __tablename__ = "ibkr_index_bar_daily_bids"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyAsks(Base):
    __tablename__ = "ibkr_index_bar_daily_asks"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyAdjusuted(Base):
    __tablename__ = "ibkr_index_bar_daily_adjusted"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyHistoricalVolatility(Base):
    __tablename__ = "ibkr_index_bar_daily_historical_volatility"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrIndexBarDailyOptionImpliedVolatility(Base):
    __tablename__ = "ibkr_index_bar_daily_option_implied_volatility"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("ibkr_index_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockInfo(Base):
    __tablename__ = "ibkr_stock_info"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock_info.id"))
    ticker_symbol = Column(String(6))
    contract_id = Column(Integer)
    primary_exchange = Column(String(32))
    exchange = Column(String(32))
    oldest_available = Column(DateTime)


class IbkrStockBarDailyTrades(Base):
    __tablename__ = "ibkr_stock_bar_daily_trades"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyBids(Base):
    __tablename__ = "ibkr_stock_bar_daily_bids"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyAsks(Base):
    __tablename__ = "ibkr_stock_bar_daily_asks"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyAdjusuted(Base):
    __tablename__ = "ibkr_stock_bar_daily_adjusted"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyHistoricalVolatility(Base):
    __tablename__ = "ibkr_stock_bar_daily_historical_volatility"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IbkrStockBarDailyOptionImpliedVolatility(Base):
    __tablename__ = "ibkr_stock_bar_daily_option_implied_volatility"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("ibkr_stock_info.id"))
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class IndexInfo(Base):
    __tablename__ = "index_info"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    name = Column(String, nullable=True, default=None)
    ibkr_symbol = Column(String, nullable=True, default=None)
    ibkr_contract_id = Column(String, nullable=True, default=None)
    ibkr_primary_exchange = Column(String, nullable=True, default=None)
    yahoo_symbol = Column(String, nullable=True, default=None)
    ipo_date = Column(DateTime, nullable=True, default=None)
    first_seen = Column(Date, nullable=True, default=None)
    last_seen = Column(Date, nullable=True, default=None)
    delisted_date = Column(Date, nullable=True, default=None)


class NasdaqEtfInfo(Base):
    __tablename__ = "nasdaq_etf_info"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    company_name = Column(String(64))
    first_seen = Column(Date,
                        server_default=func.current_timestamp(),
                        nullable=False)
    last_seen = Column(Date, nullable=False)


class NasdaqStockInfo(Base):
    __tablename__ = "nasdaq_stock_info"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    company_name = Column(String(64))
    country = Column(String(64))
    industry = Column(String(64))
    sector = Column(String(64))
    first_seen = Column(Date,
                        server_default=func.current_timestamp(),
                        nullable=False)
    last_seen = Column(Date, nullable=False)


class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(64))
    value = Column(String(64))


class StockInfo(Base):
    __tablename__ = "stock_info"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("company_info.id"))
    primary_exchange_id = Column(Integer, ForeignKey("exchange_info.id"))
    company = relationship(CompanyInfo)
    primary_exchange = relationship(ExchangeInfo)


class StockExchanges(Base):
    __tablename__ = "stock_exchanges"
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stock_info.id"))
    exchange_id = Column(Integer, ForeignKey("exchange_info.id"))
    begin_date = Column(Date)
    end_date = Column(Date)


class TimeZones(Base):
    __tablename__ = "timezones"
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    code = Column(String(8))


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
    company_id = Column(Integer, ForeignKey("company_info.id"))
    ticker = Column(String(8), nullable=False)
    oldest_available = Column(DateTime)
    delisted_date = Column(Date, nullable=True, default=None)
    first_seen = Column(Date)
    last_seen = Column(Date)


class YahooStockBarDaily(Base):
    __tablename__ = "yahoo_stock_bar_daily"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_info.id"))
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
    company_id = Column(Integer, ForeignKey("company_info.id"))
    date = Column(Date)
    dividend = Column(Float)
    date_downloaded = Column(Date,
                             server_default=func.current_timestamp(),
                             nullable=False)


class YahooStockSplits(Base):
    __tablename__ = "yahoo_stock_splits"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("company_info.id"))
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
