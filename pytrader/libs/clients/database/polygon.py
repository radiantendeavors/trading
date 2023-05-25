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
# Common Stock Tables
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


# ==================================================================================================
#
# Preferred Stock Tables
#
# ==================================================================================================
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


# ==================================================================================================
#
# Warrant Tables
#
# ==================================================================================================
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
    warrant_id = Column(Integer, foreign_key=("z_polygon_warrant_info.id"))
    warrant = relationship(PolygonWarrantInfo)
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
    warrant_id = Column(Integer, foreign_key=("z_polygon_warrant_info.id"))
    warrant = relationship(PolygonWarrantInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Right tables
#
# ==================================================================================================
class PolygonRightInfo(Base):
    __tablename__ = "z_polygon_right_info"
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


class PolygonRightDetails(Base):
    __tablename__ = "z_polygon_right_details"
    id = Column(Integer, primary_key=True)
    right_id = Column(Integer, foreign_key=("z_polygon_right_info.id"))
    right = relationship(PolygonRightInfo)
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
    __tablename__ = "z_polygon_right_delisted"
    id = Column(Integer, primary_key=True)
    right_id = Column(Integer, foreign_key=("z_polygon_right_info.id"))
    right = relationship(PolygonRightInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Corporate Bond Tables
#
# ==================================================================================================
class PolygonBondInfo(Base):
    __tablename__ = "z_polygon_bond_info"
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


class PolygonBondDetails(Base):
    __tablename__ = "z_polygon_bond_details"
    id = Column(Integer, primary_key=True)
    bond_id = Column(Integer, foreign_key=("z_polygon_bond_info.id"))
    bond = relationship(PolygonBondInfo)
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


class PolygonBondDelisted(Base):
    __tablename__ = "z_polygon_bond_delisted"
    id = Column(Integer, primary_key=True)
    bond_id = Column(Integer, foreign_key=("z_polygon_bond_info.id"))
    bond = relationship(PolygonBondInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# ETF Tables
#
# ==================================================================================================
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


# ==================================================================================================
#
# ETN Tables
#
# ==================================================================================================
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


# ==================================================================================================
#
# ETV Tables
#
# ==================================================================================================
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


# ==================================================================================================
#
# Structured Product Tables
#
# ==================================================================================================
class PolygonStructuredProductInfo(Base):
    __tablename__ = "z_polygon_structured_product_info"
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


class PolygonStructuredProductDetails(Base):
    __tablename__ = "z_polygon_structured_product_details"
    id = Column(Integer, primary_key=True)
    structured_product_id = Column(
        Integer, foreign_key=("z_polygon_structured_product_info.id"))
    structured_product = relationship(PolygonStructuredProductInfo)
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


class PolygonStructuredProductDelisted(Base):
    __tablename__ = "z_polygon_structured_product_delisted"
    id = Column(Integer, primary_key=True)
    structured_product_id = Column(
        Integer, foreign_key=("z_polygon_structured_product_info.id"))
    structured_product = relationship(PolygonStructuredProductInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# American Depository Receipt Common Tables
#
# ==================================================================================================
class PolygonAmericanDepositoryReceiptCommonInfo(Base):
    __tablename__ = "z_polygon_american_depository_receipt_common_info"
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


class PolygonAmericanDepositoryReceiptCommonDetails(Base):
    __tablename__ = "z_polygon_american_depository_receipt_common_details"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_common_id = Column(
        Integer,
        foreign_key=("z_polygon_american_depository_receipt_common_info.id"))
    american_depository_receipt_common = relationship(
        PolygonAmericanDepositoryReceiptCommonInfo)
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


class PolygonAmericanDepositoryReceiptCommonDelisted(Base):
    __tablename__ = "z_polygon_american_depository_receipt_common_delisted"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_common_id = Column(
        Integer,
        foreign_key=("z_polygon_american_depository_receipt_common_info.id"))
    american_depository_receipt_common = relationship(
        PolygonAmericanDepositoryReceiptCommonInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# ADRP Tables
#
# ==================================================================================================
class PolygonAmericanDepositoryReceiptPreferredInfo(Base):
    __tablename__ = "z_polygon_american_depository_receipt_preferred_info"
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


class PolygonAmericanDepositoryReceiptPreferredDetails(Base):
    __tablename__ = "z_polygon_american_depository_receipt_preferred_details"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_preferred_id = Column(
        Integer,
        foreign_key=(
            "z_polygon_american_depository_receipt_preferred_info.id"))
    american_depository_receipt_preferred = relationship(
        PolygonAmericanDepositoryReceiptPreferredInfo)
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


class PolygonAmericandepositoryreceiptpreferredDelisted(Base):
    __tablename__ = "z_polygon_american_depository_receipt_preferred_delisted"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_preferred_id = Column(
        Integer,
        foreign_key=(
            "z_polygon_american_depository_receipt_preferred_info.id"))
    american_depository_receipt_preferred = relationship(
        PolygonAmericanDepositoryReceiptPreferredInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# ADRW Tables
#
# ==================================================================================================
class PolygonAmericanDepositoryReceiptWarrantInfo(Base):
    __tablename__ = "z_polygon_american_depository_receipt_warrant_info"
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


class PolygonAmericanDepositoryReceiptWarrantDetails(Base):
    __tablename__ = "z_polygon_american_depository_receipt_warrant_details"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_warrant_id = Column(
        Integer,
        foreign_key=("z_polygon_american_depository_receipt_warrant_info.id"))
    american_depository_receipt_warrant = relationship(
        PolygonAmericanDepositoryReceiptWarrantInfo)
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


class PolygonAmericanDepositoryReceiptWarrantDelisted(Base):
    __tablename__ = "z_polygon_american_depository_receipt_warrant_delisted"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_warrant_id = Column(
        Integer,
        foreign_key=("z_polygon_american_depository_receipt_warrant_info.id"))
    american_depository_receipt_warrant = relationship(
        PolygonAmericanDepositoryReceiptWarrantInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# ADRR Tables
#
# ==================================================================================================
class PolygonAmericanDepositoryReceiptRightInfo(Base):
    __tablename__ = "z_polygon_american_depository_receipt_right_info"
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


class PolygonAmericanDepositoryReceiptRightDetails(Base):
    __tablename__ = "z_polygon_american_depository_receipt_right_details"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_right_id = Column(
        Integer,
        foreign_key=("z_polygon_american_depository_receipt_right_info.id"))
    american_depository_receipt_right = relationship(
        PolygonAmericanDepositoryReceiptRightInfo)
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


class PolygonAmericanDepositoryReceiptRightDelisted(Base):
    __tablename__ = "z_polygon_american_depository_receipt_right_delisted"
    id = Column(Integer, primary_key=True)
    american_depository_receipt_right_id = Column(
        Integer,
        foreign_key=("z_polygon_american_depository_receipt_right_info.id"))
    american_depository_receipt_right = relationship(
        PolygonAmericanDepositoryReceiptRightInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Fund Tables
#
# ==================================================================================================
class PolygonFundInfo(Base):
    __tablename__ = "z_polygon_fund_info"
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


class PolygonFundDetails(Base):
    __tablename__ = "z_polygon_fund_details"
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, foreign_key=("z_polygon_fund_info.id"))
    fund = relationship(PolygonFundInfo)
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


class PolygonFundDelisted(Base):
    __tablename__ = "z_polygon_fund_delisted"
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, foreign_key=("z_polygon_fund_info.id"))
    fund = relationship(PolygonFundInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Basket Tables
#
# ==================================================================================================
class PolygonBasketInfo(Base):
    __tablename__ = "z_polygon_basket_info"
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


class PolygonBasketDetails(Base):
    __tablename__ = "z_polygon_basket_details"
    id = Column(Integer, primary_key=True)
    basket_id = Column(Integer, foreign_key=("z_polygon_basket_info.id"))
    basket = relationship(PolygonBasketInfo)
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


class PolygonBasketDelisted(Base):
    __tablename__ = "z_polygon_basket_delisted"
    id = Column(Integer, primary_key=True)
    basket_id = Column(Integer, foreign_key=("z_polygon_basket_info.id"))
    basket = relationship(PolygonBasketInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Unit Tables
#
# ==================================================================================================
class PolygonUnitInfo(Base):
    __tablename__ = "z_polygon_unit_info"
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


class PolygonUnitDetails(Base):
    __tablename__ = "z_polygon_unit_details"
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, foreign_key=("z_polygon_unit_info.id"))
    unit = relationship(PolygonUnitInfo)
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


class PolygonUnitDelisted(Base):
    __tablename__ = "z_polygon_unit_delisted"
    id = Column(Integer, primary_key=True)
    unit_id = Column(Integer, foreign_key=("z_polygon_unit_info.id"))
    unit = relationship(PolygonUnitInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Liquid Trust Tables
#
# ==================================================================================================
class PolygonLiquidTrustInfo(Base):
    __tablename__ = "z_polygon_liquid_trust_info"
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


class PolygonLiquidTrustDetails(Base):
    __tablename__ = "z_polygon_liquid_trust_details"
    id = Column(Integer, primary_key=True)
    liquidtrust_id = Column(Integer,
                            foreign_key=("z_polygon_liquid_trust_info.id"))
    liquidtrust = relationship(PolygonLiquidTrustInfo)
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


class PolygonLiquidTrustDelisted(Base):
    __tablename__ = "z_polygon_liquid_trust_delisted"
    id = Column(Integer, primary_key=True)
    liquidtrust_id = Column(Integer,
                            foreign_key=("z_polygon_liquid_trust_info.id"))
    liquidtrust = relationship(PolygonLiquidTrustInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Ordinary Share Tables
#
# ==================================================================================================
class PolygonOrdinarySharesInfo(Base):
    __tablename__ = "z_polygon_ordinary_shares_info"
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


class PolygonOrdinarySharesDetails(Base):
    __tablename__ = "z_polygon_ordinary_shares_details"
    id = Column(Integer, primary_key=True)
    ordinary_shares_id = Column(
        Integer, foreign_key=("z_polygon_ordinaryshares_info.id"))
    ordinary_shares = relationship(PolygonOrdinarySharesInfo)
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


class PolygonOrdinarySharesDelisted(Base):
    __tablename__ = "z_polygon_ordinary_shares_delisted"
    id = Column(Integer, primary_key=True)
    ordinaryshares_id = Column(
        Integer, foreign_key=("z_polygon_ordinary_shares_info.id"))
    ordinaryshares = relationship(PolygonOrdinarySharesInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Global Depository Receipt Tables
#
# ==================================================================================================
class PolygonGlobalDepositoryReceiptInfo(Base):
    __tablename__ = "z_polygon_global_depository_receipt_info"
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


class PolygonGlobalDepositoryReceiptDetails(Base):
    __tablename__ = "z_polygon_global_depository_receipt_details"
    id = Column(Integer, primary_key=True)
    globaldepositoryreceipt_id = Column(
        Integer, foreign_key=("z_polygon_global_depository_receipt_info.id"))
    globaldepositoryreceipt = relationship(PolygonGlobalDepositoryReceiptInfo)
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


class PolygonGlobalDepositoryReceiptDelisted(Base):
    __tablename__ = "z_polygon_global_depository_receipt_delisted"
    id = Column(Integer, primary_key=True)
    globaldepositoryreceipt_id = Column(
        Integer, foreign_key=("z_polygon_global_depository_receipt_info.id"))
    globaldepositoryreceipt = relationship(PolygonGlobalDepositoryReceiptInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Other Tables
#
# ==================================================================================================
class PolygonOtherInfo(Base):
    __tablename__ = "z_polygon_other_info"
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


class PolygonOtherDetails(Base):
    __tablename__ = "z_polygon_other_details"
    id = Column(Integer, primary_key=True)
    other_id = Column(Integer, foreign_key=("z_polygon_other_info.id"))
    other = relationship(PolygonOtherInfo)
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


class PolygonOtherDelisted(Base):
    __tablename__ = "z_polygon_other_delisted"
    id = Column(Integer, primary_key=True)
    other_id = Column(Integer, foreign_key=("z_polygon_other_info.id"))
    other = relationship(PolygonOtherInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# New York Registry Share Tables
#
# ==================================================================================================
class PolygonNewYorkRegistryShareInfo(Base):
    __tablename__ = "z_polygon_new_york_registry_share_info"
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


class PolygonNewYorkRegistryShareDetails(Base):
    __tablename__ = "z_polygon_new_york_registry_share_details"
    id = Column(Integer, primary_key=True)
    newyorkregistryshare_id = Column(
        Integer, foreign_key=("z_polygon_new_york_registry_share_info.id"))
    newyorkregistryshare = relationship(PolygonNewYorkRegistryShareInfo)
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


class PolygonNewYorkRegistryShareDelisted(Base):
    __tablename__ = "z_polygon_new_york_registry_share_delisted"
    id = Column(Integer, primary_key=True)
    newyorkregistryshare_id = Column(
        Integer, foreign_key=("z_polygon_new_york_registry_share_info.id"))
    newyorkregistryshare = relationship(PolygonNewYorkRegistryShareInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Agency Bond Tables
#
# ==================================================================================================
class PolygonAgencyBondInfo(Base):
    __tablename__ = "z_polygon_agency_bond_info"
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


class PolygonAgencyBondDetails(Base):
    __tablename__ = "z_polygon_agency_bond_details"
    id = Column(Integer, primary_key=True)
    agencybond_id = Column(Integer,
                           foreign_key=("z_polygon_agency_bond_info.id"))
    agencybond = relationship(PolygonAgencyBondInfo)
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


class PolygonAgencyBondDelisted(Base):
    __tablename__ = "z_polygon_agency_bond_delisted"
    id = Column(Integer, primary_key=True)
    agencybond_id = Column(Integer,
                           foreign_key=("z_polygon_agency_bond_info.id"))
    agencybond = relationship(PolygonAgencyBondInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Equity Linked Bond Tables
#
# ==================================================================================================
class PolygonEquityLinkedBondInfo(Base):
    __tablename__ = "z_polygon_equity_linked_bond_info"
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


class PolygonEquityLinkedBondDetails(Base):
    __tablename__ = "z_polygon_equity_linked_bond_details"
    id = Column(Integer, primary_key=True)
    equitylinkedbond_id = Column(
        Integer, foreign_key=("z_polygon_equity_linked_bond_info.id"))
    equitylinkedbond = relationship(PolygonEquityLinkedBondInfo)
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


class PolygonEquityLinkedBondDelisted(Base):
    __tablename__ = "z_polygon_equity_linked_bond_delisted"
    id = Column(Integer, primary_key=True)
    equitylinkedbond_id = Column(
        Integer, foreign_key=("z_polygon_equity_linked_bond_info.id"))
    equitylinkedbond = relationship(PolygonEquityLinkedBondInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Single Security ETF Tables
#
# ==================================================================================================
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


# ==================================================================================================
#
# Options Tables
#
# ==================================================================================================

# ==================================================================================================
#
# Crypto Tables
#
# ==================================================================================================

# ==================================================================================================
#
# FX Tables
#
# ==================================================================================================


# ==================================================================================================
#
# Index Tables
#
# ==================================================================================================
class PolygonIndexInfo(Base):
    __tablename__ = "z_polygon_index_info"
    id = Column(Integer, primary_key=True)
    ticker_symbol = Column(String(6))
    name = Column(String(64))
    active = Column(Boolean)
    locale = Column(String(6))
    market = Column(String(6))
    source_feed = Column(String(64))


class PolygonIndexDelisted(Base):
    __tablename__ = "z_polygon_index_delisted"
    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, foreign_key=("z_polygon_index_info.id"))
    index = relationship(PolygonIndexInfo)
    delisted_utc = Column(DateTime)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def init_sqlalchemy(database_url):
    logger.debug("Begin Function")
    global engine
    engine = create_engine(database_url)
    DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    logger.debug("End Function")
