# ==================================================================================================
#
# Investing: Investing Application
#   Copyright (C) 2021  Geoff S. Derber
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# investing/lib/stocks.py
#
# ==================================================================================================
from sqlalchemy import Column, Date, ForeignKey, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Companies(Base):
    __tablename__ = "company"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ticker_id = Column(Integer)
    address_id = Column(Integer)


class CompanyBalanceSheet(Base):
    __tablename__ = "company_balance_sheet"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer)


class CompanyIncomeStatement(Base):
    __tablename__ = "company_income_statement"
    id = Colume(Integer, primary_key=True)
    company_id = Column(Integer)
