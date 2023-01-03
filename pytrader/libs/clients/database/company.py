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


@file pytrader/libs/clients/database/etf_bar_daily_raw.py
"""
from sqlalchemy import BigInteger, Boolean, Column, Date, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.database import Base

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class CompanyAddress(Base):
    __tablename__ = "company_address"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    address_id = Column(Integer, ForeignKey="address_street.id")
    beginning_date = Column(Date)
    end_date = Column(Date)


class CompanyInfo(Base):
    __tablename__ = "company_info"
    id = Column(Integer, Primary=True)
    cik = Column(Integer)
    begin_date = Column(Date)
    end_date = Column(Date)


class CompanyName(Base):
    __tablename__ = "company_name"
    id = Column(Integer, Primary=True)
    name = Column(String)
    company_id = Column(Integer, ForeignKey="company_info.id")
    begin_date = Column(Date)
    end_date = Column(Date)


class CompanySector(Base):
    __tablename__ = "company_sector"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    sector_id = Column(Integer, ForeignKey="stock_sectors.id")


class CompanyIndustry(Base):
    __tablename__ = "company_industry"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    industry_id = Column(Integer, ForeignKey="stock_industries.id")


class CompanyStockListing(Base):
    __tablename__ = "company_stock_listing"
    id = Column(Integer, Primary=True)
    company_id = Column(Integer, ForeignKey="company_info.id")
    ipo_date = Column(Date)
    delisting_date = Column(Date)
