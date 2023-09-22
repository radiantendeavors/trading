"""!
@package pytrader.libs.clients.database.ibkr

Defines the database schema, and creates the database tables for Interactive Brokers related
information.

@author G. S. Derber
@date 2022-2023
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
from datetime import date, datetime

# 3rd Party Libraries
from sqlalchemy import (BigInteger, Boolean, Date, DateTime, FetchedValue,
                        Float, ForeignKey, Integer, MetaData, String, Time,
                        select)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# Application Libraries
from pytrader.libs.clients.database.sqlalchemy.base import Base
from pytrader.libs.system import logging

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

# bigint = Annotated(int, "bigint")
# my_metadata = MetaData()


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrEtfContracts(Base):
    __tablename__ = "z_ibkr_etf_contracts"
    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(index=True, unique=True)
    ticker_symbol: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    security_type: Mapped[str] = mapped_column(String(6))
    exchange: Mapped[str] = mapped_column(String(12), nullable=False, default="SMART")
    currency: Mapped[str] = mapped_column(String(32), nullable=False)
    local_symbol: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    primary_exchange: Mapped[str] = mapped_column(String(32), nullable=False)
    trading_class: Mapped[str] = mapped_column(String(6))
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrEtfContracts(
            id={self.id!r},
            contract_id={self.contract_id!r},
            ticker_symbol={self.ticker_symbol!r},
            exchange={self.exchange!r},
            primary_exchange{self.primary_exchange!r}
        )
        """
        return repr_str

    def query_contract(self, db_session, local_symbol):
        logger.debug10("Begin Funtion")
        query = select(IbkrEtfContracts).where(IbkrEtfContracts.local_symbol == local_symbol)

        results = db_session.execute(query).one()

        logger.debug("Results: %s", results)
        logger.debug10("End Function")
        return results

    def query_contracts(self, db_session):
        logger.debug10("Begin Funtion")
        query = select(IbkrEtfContracts)
        results = db_session.execute(query).all()

        logger.debug("Results: %s", results)
        logger.debug10("End Function")
        return results

    def row_exists(self, db_session, local_symbol):
        ticker_list = self.query_contract(db_session, local_symbol)

        if len(ticker_list) == 0:
            return False
        else:
            return True

    def insert(self, db_session, contract_id, ticker_symbol, security_type, exchange, currency,
               local_symbol, primary_exchange, trading_class):
        self.contract_id = contract_id
        self.ticker_symbol = ticker_symbol
        self.security_type = security_type
        self.exchange = exchange
        self.currency = currency
        self.local_symbol = local_symbol
        self.primary_exchange = primary_exchange
        self.trading_class = trading_class

        row_exists = self.row_exists(db_session, ticker_symbol)

        if not row_exists:
            try:
                db_session.add(self)
            except Exception as msg:
                logger.error("Exception: %s", msg)
                print("Error Adding Ticker:", self.ticker)

            try:
                db_session.commit()
            except Exception as msg:
                logger.error("Exception: %s", msg)
                print("Error committing ticker:", self.ticker)

        return None


class IbkrEtfBarHistoryBeginDate(Base):
    __tablename__ = "z_ibkr_etf_history_begin_date"
    id: Mapped[int] = mapped_column(primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    oldest_datetime: Mapped[datetime]
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrEtfBarHistoryBeginDate(
            id={self.id!r},
            ibkr_etf_id={self.ibkr_etf_id!r},
            oldest_datetime={self.oldest_datetime!r},
            last_updated={self.last_updated!r}
        )
        """
        return repr_str

    def query_begin_date(self, db_session, ibkr_contract):
        logger.debug10("Begin Function")
        query = select(IbkrEtfBarHistoryBeginDate).where(
            IbkrEtfBarHistoryBeginDate.ibkr_contract == ibkr_contract)

        results = db_session.execute(query).one()
        logger.debug("Results: %s", results)
        logger.debug10("End Function")
        return results[0].oldest_datetime

    def row_exists(self, db_session):
        date_list = []
        date_list = self.select(db_session, self.ibkr_contract)

        if len(date_list) == 0:
            return False
        else:
            return True

    def insert(self, db_session, oldest_datetime):
        self.oldest_datetime = oldest_datetime

        row_exists = self.row_exists(db_session)
        if not row_exists:
            try:
                db_session.add(self)
            except Exception as msg:
                logger.error("Exception: %s", msg)
                print("Error Adding Ticker:", self.ibkr_contract)

            try:
                db_session.commit()
            except Exception as msg:
                logger.error("Exception: %s", msg)
                print("Error committing ticker:", self.ibkr_contract)


class IbkrEtfContractDetails(Base):
    __tablename__ = "z_ibkr_etf_contract_details"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    market_name: Mapped[str] = mapped_column(String(6))
    min_tick: Mapped[float]
    price_magnifier: Mapped[int]
    long_name: Mapped[str] = mapped_column(String(96))
    timezone_id: Mapped[str] = mapped_column(String(16))
    stock_type: Mapped[str] = mapped_column(String(16))
    aggregated_group: Mapped[int]


class IbkrEtfExchanges(Base):
    __tablename__ = "z_ibkr_etf_exchanges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    exchange: Mapped[str] = mapped_column(String(12))


class IbkrEtfOrderTypes(Base):
    __tablename__ = "z_ibkr_etf_order_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    order_type: Mapped[str] = mapped_column(String(12))


class IbkrEtfTradingHours(Base):
    __tablename__ = "z_ibkr_etf_trading_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    trading_hours: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrEtfLiquidHours(Base):
    __tablename__ = "z_ibkr_etf_liquid_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    liquid_hours: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrEtfOptionParams(Base):
    __tablename__ = "z_ibkr_etf_option_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    exchange: Mapped[str] = mapped_column(String(12))


class IbkrEtfBar1MinTrades(Base):
    __tablename__ = "z_ibkr_etf_bar_1min_trades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    bar_open: Mapped[float]
    bar_high: Mapped[float]
    bar_low: Mapped[float]
    bar_close: Mapped[float]
    bar_volume: Mapped[int]
    bar_count: Mapped[float]
    outside_trading_hours: Mapped[bool]
    date_downloaded: Mapped[date] = mapped_column(server_default=func.current_timestamp())


# class IbkrEtfBar1MinBids(Base):
#     __tablename__ = "z_ibkr_etf_bar_1min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1MinAsks(Base):
#     __tablename__ = "z_ibkr_etf_bar_1min_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1MinAdjusted(Base):
#     __tablename__ = "z_ibkr_etf_bar_1min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1MinHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_1min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1MinOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_1min_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())


class IbkrEtfBar5SecTrades(Base):
    __tablename__ = "z_ibkr_etf_bar_5sec_trades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_etf_contracts.id"))
    ibkr_contract: Mapped["IbkrEtfContracts"] = relationship()
    date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    bar_open: Mapped[float]
    bar_high: Mapped[float]
    bar_low: Mapped[float]
    bar_close: Mapped[float]
    bar_volume: Mapped[int]
    bar_count: Mapped[float]
    outside_trading_hours: Mapped[bool]
    date_downloaded: Mapped[date] = mapped_column(server_default=func.current_timestamp())


# class IbkrEtfBar5minTrades(Base):
#     __tablename__ = "z_ibkr_etf_bar_5min_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[float]
#     count: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar5minBids(Base):
#     __tablename__ = "z_ibkr_etf_bar_5min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar5minAsks(Base):
#     __tablename__ = "z_ibkr_etf_bar_5min_asks"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar5minAdjusted(Base):
#     __tablename__ = "z_ibkr_etf_bar_5min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar5minHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_5min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar5minOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_5min_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar15minTrades(Base):
#     __tablename__ = "z_ibkr_etf_bar_15min_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     count: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar15minBids(Base):
#     __tablename__ = "z_ibkr_etf_bar_15min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar15minAsks(Base):
#     __tablename__ = "z_ibkr_etf_bar_15min_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar15minAdjusted(Base):
#     __tablename__ = "z_ibkr_etf_bar_15min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int] = mapped_column(Integer)
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar15minHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_15min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar15minOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_15min_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar30minTrades(Base):
#     __tablename__ = "z_ibkr_etf_bar_30min_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     count: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar30minBids(Base):
#     __tablename__ = "z_ibkr_etf_bar_30min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar30minAsks(Base):
#     __tablename__ = "z_ibkr_etf_bar_30min_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar30minAdjusted(Base):
#     __tablename__ = "z_ibkr_etf_bar_30min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar30minHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_30min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar30minOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_30miny_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1hrTrades(Base):
#     __tablename__ = "z_ibkr_etf_bar_1hr_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     count: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1hrBids(Base):
#     __tablename__ = "z_ibkr_etf_bar_1hr_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1hrAsks(Base):
#     __tablename__ = "z_ibkr_etf_bar_1hr_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1hrAdjusted(Base):
#     __tablename__ = "z_ibkr_etf_bar_1hr_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1hrHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_1hr_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBar1hrOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_1hr_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBarDailyTrades(Base):
#     __tablename__ = "z_ibkr_etf_bar_daily_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     count: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBarDailyBids(Base):
#     __tablename__ = "z_ibkr_etf_bar_daily_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool] = mapped_column(Boolean)
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBarDailyAsks(Base):
#     __tablename__ = "z_ibkr_etf_bar_daily_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBarDailyAdjusted(Base):
#     __tablename__ = "z_ibkr_etf_bar_daily_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBarDailyHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_daily_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrEtfBarDailyOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_etf_bar_daily_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_etf_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_etf_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())
