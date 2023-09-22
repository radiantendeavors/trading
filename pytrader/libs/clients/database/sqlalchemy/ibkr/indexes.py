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
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrIndexContracts(Base):
    __tablename__ = "z_ibkr_index_contracts"
    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(index=True, unique=True)
    ticker_symbol: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    security_type: Mapped[str] = mapped_column(String(6))
    exchange: Mapped[str] = mapped_column(String(12), nullable=False, default="SMART")
    currency: Mapped[str] = mapped_column(String(32), nullable=False)
    local_symbol: Mapped[str] = mapped_column(String(6), index=True, unique=True)
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())


class IbkrIndexContractDetails(Base):
    __tablename__ = "z_ibkr_index_contract_details"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_index_contracts.id"))
    ibkr_contract: Mapped["IbkrIndexContracts"] = relationship()
    market_name: Mapped[str] = mapped_column(String(6))
    min_tick: Mapped[float]
    price_magnifier: Mapped[int]
    long_name: Mapped[str] = mapped_column(String(96))
    industry: Mapped[str] = mapped_column(String(32))
    category: Mapped[str] = mapped_column(String(32))
    subcategory: Mapped[str] = mapped_column(String(32))
    timezone_id: Mapped[str] = mapped_column(String(16))
    aggregated_group: Mapped[int]


class IbkrIndexExchanges(Base):
    __tablename__ = "z_ibkr_index_exchanges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_index_contracts.id"))
    ibkr_contract: Mapped["IbkrIndexContracts"] = relationship()
    exchange: Mapped[str] = mapped_column(String(12))


class IbkrIndexOrderTypes(Base):
    __tablename__ = "z_ibkr_index_order_types"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_index_contracts.id"))
    ibkr_contract: Mapped["IbkrIndexContracts"] = relationship()
    order_type: Mapped[str] = mapped_column(String(12))


class IbkrIndexTradingHours(Base):
    __tablename__ = "z_ibkr_index_trading_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_index_contracts.id"))
    ibkr_contract: Mapped["IbkrIndexContracts"] = relationship()
    trading_hours: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrIndexLiquidHours(Base):
    __tablename__ = "z_ibkr_index_liquid_hours"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_index_contracts.id"))
    ibkr_contract: Mapped["IbkrIndexContracts"] = relationship()
    liquid_hours: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class IbkrIndexBarHistoryBeginDate(Base):
    __tablename__ = "z_ibkr_index_history_begin_date"
    id: Mapped[int] = mapped_column(primary_key=True)
    ibkr_contract_id: Mapped[int] = mapped_column(ForeignKey("z_ibkr_index_contracts.id"))
    ibkr_contract: Mapped["IbkrIndexContracts"] = relationship()
    oldest_datetime: Mapped[datetime]
    last_updated: Mapped[date] = mapped_column(server_default=func.current_timestamp())

    def __repr__(self) -> str:
        repr_str = f"""
        IbkrIndexBarHistoryBeginDate(
            id={self.id!r},
            ibkr_contract_id={self.ibkr_index_id!r},
            oldest_datetime={self.oldest_datetime!r},
            last_updated={self.last_updated!r}
        )
        """
        return repr_str

    def query_begin_date(self, db_session, ibkr_contract):
        logger.debug10("Begin Function")
        query = select(IbkrIndexBarHistoryBeginDate).where(
            IbkrIndexBarHistoryBeginDate.ibkr_index == ibkr_contract)

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


# class IbkrIndexBarDailyTrades(Base):
#     __tablename__ = "z_ibkr_index_bar_daily_trades"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     index_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_index_info.id"))
#     index = relationship(IbkrIndexContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     volume: Mapped[] = mapped_column(BigInteger)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrIndexBarDailyBids(Base):
#     __tablename__ = "z_ibkr_index_bar_daily_bids"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     index_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_index_info.id"))
#     index = relationship(IbkrIndexContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrIndexBarDailyAsks(Base):
#     __tablename__ = "z_ibkr_index_bar_daily_asks"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     index_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_index_info.id"))
#     index = relationship(IbkrIndexContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrIndexBarDailyAdjusted(Base):
#     __tablename__ = "z_ibkr_index_bar_daily_adjusted"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     index_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_index_info.id"))
#     index = relationship(IbkrIndexContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     volume: Mapped[] = mapped_column(BigInteger)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrIndexBarDailyHistoricalVolatility(Base):
#     __tablename__ = "z_ibkr_index_bar_daily_historical_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     index_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_index_info.id"))
#     index = relationship(IbkrIndexContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)

# class IbkrIndexBarDailyOptionImpliedVolatility(Base):
#     __tablename__ = "z_ibkr_index_bar_daily_option_implied_volatility"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     index_id: Mapped[] = mapped_column(Integer, ForeignKey("z_ibkr_index_info.id"))
#     index = relationship(IbkrIndexContract)
#     date: Mapped[] = mapped_column(Date)
#     bar_open: Mapped[] = mapped_column(Float)
#     bar_high: Mapped[] = mapped_column(Float)
#     bar_low: Mapped[] = mapped_column(Float)
#     bar_close: Mapped[] = mapped_column(Float)
#     date_downloaded: Mapped[] = mapped_column(Date,
#                              server_default=func.current_timestamp(),
#                              nullable=False)
