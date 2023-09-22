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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
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
class IbkrStockContracts(Base):
    __tablename__ = "z_ibkr_stock_contracts"
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
        IbkrStockContracts(
            id={self.id!r},
            contract_id={self.contract_id!r},
            ticker_symbol={self.ticker_symbol!r}
        )
        """
        return repr_str

    def query_contract(self, db_session, local_symbol):
        logger.debug10("Begin Funtion")
        query = select(IbkrStockContracts).where(IbkrStockContracts.local_symbol == local_symbol)

        results = db_session.execute(query).one()

        logger.debug("Results: %s", results)
        logger.debug10("End Function")
        return results

    def query_contracts(self, db_session):
        logger.debug10("Begin Funtion")
        query = select(IbkrStockContracts)
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


class IbkrStockContractDetails(Base):
    __tablename__ = "z_ibkr_stock_contract_details"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stock_contracts.id"))
    ibkr_contract: Mapped["IbkrStockContracts"] = relationship()
    market_name: Mapped[str] = mapped_column(String(6))
    min_tick: Mapped[float]
    price_magnifier: Mapped[int]
    long_name: Mapped[str] = mapped_column(String(96))
    industry: Mapped[str] = mapped_column(String(32))
    category: Mapped[str] = mapped_column(String(32))
    subcategory: Mapped[str] = mapped_column(String(32))
    timezone_id: Mapped[str] = mapped_column(String(16))
    stock_type: Mapped[str] = mapped_column(String(16))
    aggregated_group: Mapped[int]


class IbkrStockExchanges(Base):
    __tablename__ = "z_ibkr_stock_exchanges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stock_contracts.id"))
    ibkr_contract: Mapped["IbkrStockContracts"] = relationship()
    exchange: Mapped[str] = mapped_column(String(12))


class IbkrStockOrderTypes(Base):
    __tablename__ = "z_ibkr_stock_order_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stock_contracts.id"))
    ibkr_contract: Mapped["IbkrStockContracts"] = relationship()
    order_type: Mapped[str] = mapped_column(String(12))


class IbkrStockTradingHours(Base):
    __tablename__ = "z_ibkr_stock_trading_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stock_contracts.id"))
    ibkr_contract: Mapped["IbkrStockContracts"] = relationship()
    trading_hours: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrStockLiquidHours(Base):
    __tablename__ = "z_ibkr_stock_liquid_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stock_contracts.id"))
    ibkr_contract: Mapped["IbkrStockContracts"] = relationship()
    liquid_hours: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrStockHistoryBeginDate(Base):
    __tablename__ = "z_ibkr_stock_history_begin_date"
    id: Mapped[int] = mapped_column(primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_stock_contracts.id"))
    ibkr_contract: Mapped["IbkrStockContracts"] = relationship()
    oldest_datetime: Mapped[datetime]
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrStockBarHistoryBeginDate(
            id={self.id!r},
            ibkr_contract_id={self.ibkr_etf_id!r},
            oldest_datetime={self.oldest_datetime!r},
            last_updated={self.last_updated!r}
        )
        """
        return repr_str

    def query_begin_date(self, db_session, ibkr_contract):
        logger.debug10("Begin Function")
        query = select(IbkrStockHistoryBeginDate).where(
            IbkrStockHistoryBeginDate.ibkr_contract == ibkr_contract)

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


# class IbkrStockContract(Base):
#     __tablename__ = "z_ibkr_stock_info"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     ticker_symbol: Mapped[] = mapped_column(String(6))
#     contract_id: Mapped[] = mapped_column(Integer)
#     primary_exchange: Mapped[] = mapped_column(String(32))
#     exchange: Mapped[] = mapped_column(String(32))
#     oldest_available: Mapped[] = mapped_column(DateTime)

# class IbkrStockBarDailyTrades(Base):
#     __tablename__ = "z_ibkr_stock_bar_daily_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stock_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stock_info.id"))
#     stock = relationship(IbkrStockContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     volume: Mapped[] = mapped_column(BigInteger)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStockBarDailyBids(Base):
#     __tablename__ = "z_ibkr_stock_bar_daily_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stock_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stock_info.id"))
#     stock = relationship(IbkrStockContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStockBarDailyAsks(Base):
#     __tablename__ = "z_ibkr_stock_bar_daily_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stock_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stock_info.id"))
#     stock = relationship(IbkrStockContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStockBarDailyAdjusted(Base):
#     __tablename__ = "z_ibkr_stock_bar_daily_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stock_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stock_info.id"))
#     stock = relationship(IbkrStockContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     volume: Mapped[] = mapped_column(BigInteger)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStockBarDailyHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_stock_bar_daily_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stock_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stock_info.id"))
#     stock = relationship(IbkrStockContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrStockBarDailyOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_stock_bar_daily_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     stock_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_stock_info.id"))
#     stock = relationship(IbkrStockContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)
