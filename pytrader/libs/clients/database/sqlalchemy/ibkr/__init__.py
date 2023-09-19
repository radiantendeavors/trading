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
from datetime import date

# 3rd Party Libraries
from sqlalchemy import (BigInteger, Boolean, Date, DateTime, FetchedValue,
                        Float, ForeignKey, Integer, MetaData, String, Time,
                        select)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

# Application Libraries
from pytrader.libs.clients.database.sqlalchemy import base
from pytrader.libs.clients.database.sqlalchemy.ibkr import (etfs, indexes,
                                                            stocks)
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
class IbkrContractListing(base.Base):
    __tablename__ = "z_ibkr_contract_listing"
    id: Mapped[int] = mapped_column(primary_key=True)
    long_id: Mapped[str] = mapped_column(String(160), index=True, unique=True)
    ib_symbol: Mapped[str] = mapped_column(String(32))
    product_description: Mapped[str] = mapped_column(String(96))
    symbol: Mapped[str] = mapped_column(String(32))
    currency: Mapped[str] = mapped_column(String(4))
    asset_class: Mapped[str] = mapped_column(String(8))
    exchange: Mapped[str] = mapped_column(String(16))
    first_seen: Mapped[date] = mapped_column(server_default=func.current_timestamp())
    last_seen: Mapped[date] = mapped_column(server_default=func.current_timestamp())


class IbkrDBTables(object):
    """!
    Manages the Interactive Broker DB Tables
    """

    def create_tables(self) -> None:
        """!
        Creates the Interactive Brokers DB Tables.

        @return None
        """
        logger.debug("Creating Tables")

        # Yes I know checkfirst defaults to true.  I wanted it to be explicit.
        base.Base.metadata.create_all(self.engine, checkfirst=True)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
