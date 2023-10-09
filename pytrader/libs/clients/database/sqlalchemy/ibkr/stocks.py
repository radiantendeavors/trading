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
from sqlalchemy import (BigInteger, DateTime, ForeignKey, Integer, String,
                        Text, select)
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
## The base logger.
logger = logging.getLogger(__name__)

# bigint = Annotated(int, "bigint")
# my_metadata = MetaData()


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrStkContracts(Base):
    __tablename__ = "z_ibkr_stk_contracts"
    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(index=True, unique=True)
    symbol: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    security_type: Mapped[str] = mapped_column(String(6))
    exchange: Mapped[str] = mapped_column(String(12), nullable=False, default="SMART")
    currency: Mapped[str] = mapped_column(String(4), nullable=False)
    local_symbol: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    primary_exchange: Mapped[str] = mapped_column(String(12), nullable=False)
    trading_class: Mapped[str] = mapped_column(String(6))
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrStkContracts(
            id={self.id!r},
            contract_id={self.contract_id!r},
            ticker_symbol={self.ticker_symbol!r}
        )
        """
        return repr_str

    def query_contract(self, db_session, local_symbol):
        logger.debug10("Begin Funtion")
        query = select(IbkrStkContracts).where(IbkrStkContracts.local_symbol == local_symbol)

        results = db_session.execute(query).one()

        logger.debug("Results: %s", results)
        logger.debug10("End Function")
        return results

    def query_contracts(self, db_session):
        logger.debug10("Begin Funtion")
        query = select(IbkrStkContracts)
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


class IbkrStkContractDetails(Base):
    __tablename__ = "z_ibkr_stk_contract_details"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stk_contracts.id"))
    ibkr_contract: Mapped["IbkrStkContracts"] = relationship()
    market_name: Mapped[str] = mapped_column(String(6))
    min_tick: Mapped[float]
    price_magnifier: Mapped[int]
    order_types: Mapped[str] = mapped_column(Text)
    valid_exchanges: Mapped[str] = mapped_column(Text)
    long_name: Mapped[str] = mapped_column(String(96))
    industry: Mapped[str] = mapped_column(String(32), nullable=True)
    category: Mapped[str] = mapped_column(String(32), nullable=True)
    subcategory: Mapped[str] = mapped_column(String(32), nullable=True)
    timezone_id: Mapped[str] = mapped_column(String(16))
    ev_multiplier: Mapped[int]
    agg_group: Mapped[int]
    sec_id_list: Mapped[str] = mapped_column(Text)
    market_rule_ids: Mapped[str] = mapped_column(Text)
    stk_type: Mapped[str] = mapped_column(String(16))


class IbkrStkTradingHours(Base):
    __tablename__ = "z_ibkr_stk_trading_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stk_contracts.id"))
    ibkr_contract: Mapped["IbkrStkContracts"] = relationship()
    begin_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class IbkrStkLiquidHours(Base):
    __tablename__ = "z_ibkr_stk_liquid_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stk_contracts.id"))
    ibkr_contract: Mapped["IbkrStkContracts"] = relationship()
    begin_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_dt: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class IbkrStkHistoryBeginDate(Base):
    __tablename__ = "z_ibkr_stk_history_begin_date"
    id: Mapped[int] = mapped_column(primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stk_contracts.id"))
    ibkr_contract: Mapped["IbkrStkContracts"] = relationship()
    oldest_datetime: Mapped[datetime]
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrStkBarHistoryBeginDate(
            id={self.id!r},
            ibkr_contract_id={self.ibkr_contract_id!r},
            oldest_datetime={self.oldest_datetime!r},
            last_updated={self.last_updated!r}
        )
        """
        return repr_str

    def query_begin_date(self, db_session, ibkr_contract):
        logger.debug10("Begin Function")
        query = select(IbkrStkHistoryBeginDate).where(
            IbkrStkHistoryBeginDate.ibkr_contract == ibkr_contract)

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

        # row_exists = self.row_exists(db_session)
        row_exists = False

        if not row_exists:
            try:
                db_session.add(self)
            except Exception as msg:
                logger.error("Exception: %s", msg)
                print("Error Adding Ticker:", self.ibkr_etf)

            try:
                db_session.commit()
            except Exception as msg:
                logger.error("Exception: %s", msg)
                print("Error committing ticker:", self.ibkr_etf)


class IbkrStkNoHistory(Base):
    __tablename__ = "z_ibkr_stk_no_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stk_contracts.id"))
    ibkr_contract: Mapped["IbkrStkContracts"] = relationship()
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())


class IbkrStkOptionParams(Base):
    __tablename__ = "z_ibkr_stk_option_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stk_contracts.id"))
    ibkr_contract: Mapped["IbkrStkContracts"] = relationship()
    exchange: Mapped[str] = mapped_column(String(12))
    multiplier: Mapped[int]
    expirations: Mapped[str] = mapped_column(Text)
    strikes: Mapped[str] = mapped_column(Text)
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())


# class IbkrStkBarDailyTrades(Base):
#     __tablename__ = "z_ibkr_stk_bar_daily_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stk_contracts.id"))
#     ibkr_contract: Mapped["IbkrStkContracts"] = relationship()
#     exchange: Mapped[str] = mapped_column(String(12))
#     date: Mapped[date]
#     bar_open: Mapped[float]
#     bar_high: Mapped[float]
#     bar_low: Mapped[float]
#     bar_close: Mapped[float]
#     bar_volume: Mapped[int] = mapped_column(BigInteger)
#     bar_wap: Mapped[float]
#     bar_count: Mapped[int] = mapped_column(BigInteger)
#     regular_trading_hours: Mapped[bool]
#     date_downloaded: Mapped[date] = mapped_column(server_default=func.current_timestamp())

# class IbkrStkBarDailyBids(Base):
#     __tablename__ = "z_ibkr_stk_bar_daily_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stk_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stk_info.id"))
#     stk = relationship(IbkrStkContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStkBarDailyAsks(Base):
#     __tablename__ = "z_ibkr_stk_bar_daily_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stk_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stk_info.id"))
#     stk = relationship(IbkrStkContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStkBarDailyAdjusted(Base):
#     __tablename__ = "z_ibkr_stk_bar_daily_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stk_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stk_info.id"))
#     stk = relationship(IbkrStkContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     volume: Mapped[] = mapped_column(BigInteger)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStkBarDailyHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_stk_bar_daily_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stk_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stk_info.id"))
#     stk = relationship(IbkrStkContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStkBarDailyOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_stk_bar_daily_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stk_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stk_info.id"))
#     stk = relationship(IbkrStkContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)
