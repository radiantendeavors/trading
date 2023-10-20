"""!
@package pytrader.libs.clients.database.sqlalchemy.ibkr.etfs

Defines the database schema, and creates the database tables for Interactive Brokers related
information.

@author G S Derber
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


@file pytrader/libs/clients/database/sqlalchemy/ibkr/etfs.py
"""

# System Libraries
from datetime import date, datetime, time

# 3rd Party Libraries
from sqlalchemy import (BigInteger, Date, DateTime, Float, ForeignKey, Integer,
                        String, Text, Time, select)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# Application Libraries
from pytrader.libs.clients.database.sqlalchemy.base import Base
from pytrader.libs.clients.database.sqlalchemy.ibkr.indexes import \
    IbkrIndContracts
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrIndOptContracts(Base):
    __tablename__ = "z_ibkr_ind_opt_contracts"
    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(index=True, unique=True)
    local_symbol: Mapped[str] = mapped_column(String(32), index=True, unique=True)
    symbol: Mapped[str] = mapped_column(String(6))
    security_type: Mapped[str] = mapped_column(String(6))
    last_trading_date: Mapped[date]
    strike: Mapped[float]
    opt_right: Mapped[str] = mapped_column(String(1))
    multiplier: Mapped[int]
    exchange: Mapped[str] = mapped_column(String(12), nullable=False, default="SMART")
    currency: Mapped[str] = mapped_column(String(4), nullable=False)
    trading_class: Mapped[str] = mapped_column(String(6))
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrIndOptContracts(
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
        query = select(IbkrIndOptContracts).where(IbkrIndOptContracts.local_symbol == local_symbol)
        results = db_session.execute(query).one()

        logger.debug("Results: %s", results)
        logger.debug10("End Function")
        return results

    def query_contracts(self, db_session):
        logger.debug10("Begin Funtion")
        query = select(IbkrIndOptContracts)
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


class IbkrIndOptContractDetails(Base):
    __tablename__ = "z_ibkr_ind_opt_contract_details"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
    ibkr_contract: Mapped["IbkrIndOptContracts"] = relationship()
    market_name: Mapped[str] = mapped_column(String(6))
    min_tick: Mapped[float]
    price_magnifier: Mapped[int]
    order_types: Mapped[str] = mapped_column(Text)
    valid_exchanges: Mapped[str] = mapped_column(Text)
    underlying_contract_id: Mapped[int] = mapped_column(
        ForeignKey("z_ibkr_ind_contracts.contract_id"))
    underlying_contract: Mapped["IbkrIndContracts"] = relationship()
    contract_month: Mapped[date]
    timezone_id: Mapped[str] = mapped_column(String(16))
    ev_multiplier: Mapped[int]
    agg_group: Mapped[int]
    sec_id_list: Mapped[str] = mapped_column(Text, nullable=True)
    market_rule_ids: Mapped[str] = mapped_column(Text)
    real_expiration_date: Mapped[date]
    last_trade_time: Mapped[time] = mapped_column(Time, nullable=True)


class IbkrIndOptTradingHours(Base):
    __tablename__ = "z_ibkr_ind_opt_trading_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
    ibkr_contract: Mapped["IbkrIndOptContracts"] = relationship()
    begin_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrIndOptLiquidHours(Base):
    __tablename__ = "z_ibkr_ind_opt_liquid_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
    ibkr_contract: Mapped["IbkrIndOptContracts"] = relationship()
    begin_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_dt: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrIndOptInvalidContracts(Base):
    __tablename__ = "z_ibkr_ind_opt_invalid_contracts"
    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(6))
    last_trading_date: Mapped[date]
    strike: Mapped[float]
    opt_right: Mapped[str] = mapped_column(String(1))
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())


class IbkrIndOptBarHistoryBeginDate(Base):
    __tablename__ = "z_ibkr_ind_opt_history_begin_date"
    id: Mapped[int] = mapped_column(primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
    ibkr_contract: Mapped["IbkrIndOptContracts"] = relationship()
    oldest_datetime: Mapped[datetime]
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrIndOptBarHistoryBeginDate(
            id={self.id!r},
            ibkr_ind_opt_id={self.ibkr_ind_opt_id!r},
            oldest_datetime={self.oldest_datetime!r},
            last_updated={self.last_updated!r}
        )
        """
        return repr_str

    def query_begin_date(self, db_session, ibkr_contract):
        logger.debug10("Begin Function")
        query = select(IbkrIndOptBarHistoryBeginDate).where(
            IbkrIndOptBarHistoryBeginDate.ibkr_contract == ibkr_contract)

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


class IbkrIndOptNoHistory(Base):
    __tablename__ = "z_ibkr_ind_opt_no_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
    ibkr_contract: Mapped["IbkrIndOptContracts"] = relationship()
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())


# class IbkrIndOptBarDailyTrades(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_daily_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     exchange: Mapped[str] = mapped_column(String(12))
#     date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     bar_volume: Mapped[int] = mapped_column(BigInteger)
#     bar_wap: Mapped[float]
#     bar_count: Mapped[int] = mapped_column(BigInteger)
#     regular_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(server_default=func.current_timestamp())

# class IbkrIndOptBar1MinTrades(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1min_trades"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     ibkr_contract: Mapped["IbkrIndOptContracts"] = relationship()
#     exchange: Mapped[str] = mapped_column(String(12))
#     date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     bar_volume: Mapped[int] = mapped_column(BigInteger)
#     bar_wap: Mapped[float]
#     bar_count: Mapped[int] = mapped_column(BigInteger)
#     regular_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(server_default=func.current_timestamp())

# class IbkrIndOptBar1MinBids(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1MinAsks(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1min_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1MinAdjusted(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1MinHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1MinIndOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1min_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar5SecTrades(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_5sec_trades"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     ibkr_contract: Mapped["IbkrIndOptContracts"] = relationship()
#     exchange: Mapped[str] = mapped_column(String(12))
#     date_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     bar_volume: Mapped[int] = mapped_column(BigInteger)
#     bar_wap: Mapped[float]
#     bar_count: Mapped[int] = mapped_column(BigInteger)
#     regular_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(server_default=func.current_timestamp())

# class IbkrIndOptBar5minTrades(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_5min_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
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

# class IbkrIndOptBar5minBids(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_5min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar5minAsks(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_5min_asks"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar5minAdjusted(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_5min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar5minHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_5min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar5minIndOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_5min_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar15minTrades(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_15min_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
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

# class IbkrIndOptBar15minBids(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_15min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar15minAsks(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_15min_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar15minAdjusted(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_15min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int] = mapped_column(Integer)
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar15minHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_15min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar15minIndOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_15min_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar30minTrades(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_30min_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
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

# class IbkrIndOptBar30minBids(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_30min_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar30minAsks(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_30min_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar30minAdjusted(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_30min_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar30minHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_30min_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar30minIndOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_30miny_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1hrTrades(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1hr_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
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

# class IbkrIndOptBar1hrBids(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1hr_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1hrAsks(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1hr_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1hrAdjusted(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1hr_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1hrHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1hr_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBar1hrIndOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_1hr_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date_time: Mapped[datetime]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBarDailyBids(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_daily_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool] = mapped_column(Boolean)
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBarDailyAsks(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_daily_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBarDailyAdjusted(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_daily_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     volume: Mapped[int]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBarDailyHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_daily_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())

# class IbkrIndOptBarDailyOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_ind_opt_bar_daily_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_ind_opt_id: Mapped[int] = mapped_column(
#         ForeignKey("z_ibkr_ind_opt_contracts.id"))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     outside_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(
#         server_default=func.current_timestamp())
