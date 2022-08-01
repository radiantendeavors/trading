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
# investing/lib/etfs.py
#
# ==================================================================================================
from datetime import date
from sqlalchemy import Column, Date, DateTime, ForeignKey, Float, Integer, String, BigInteger, Boolean
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import registry, relationship
from sqlalchemy.orm import sessionmaker, scoped_session

from pytrader.libs.util import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
#mapper_registry = registry()
Base = declarative_base()
DBSession = scoped_session(sessionmaker())


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
#@mapper_registry.mapped
class EtfInfo(Base):
    __tablename__ = "etf_info"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ticker = Column(String(6), nullable=False, unique=True)
    first_listed = Column(Date, nullable=True)
    delisted_date = Column(Date, nullable=True)
    last_seen = Column(Date, nullable=True)

    def __repr__(self):
        return "<EtfInfo(ticker='%s', last_seen='%s')" % (self.ticker,
                                                          self.last_seen)

    def add_etf_info(self, *args, **kwargs):
        if "ticker" not in kwargs:
            print("Error: Ticker is undefined")
        else:
            self.ticker = kwargs["ticker"]
            self.last_seen = date.today()

            if "^" not in self.ticker:
                try:
                    DBSession.add(self)
                except:
                    print("Error Adding Ticker:", self.ticker)
                try:
                    DBSession.commit()
                except:
                    print("Error committing ticker:", self.ticker)

        return None

    def get_ticker_list(self, *args, **kwargs):
        ticker_list = []
        ticker_object = DBSession.query(EtfInfo).filter_by(
            last_seen=date.today()).all()

        for item in ticker_object:
            ticker_list.append(item.ticker)

        return ticker_list


#@mapper_registry.mapped
class EtfWeekly(Base):
    __tablename__ = "etf_weekly"
    __tablename__ = "etf_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(6), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)


class EtfDaily(Base):
    __tablename__ = "etf_daily"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(6), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    split = Column(Float, nullable=True)
    dividends = Column(Float, nullable=True)
    shares_outstanding = Column(BigInteger, nullable=True)
    shares_float = Column(Integer, nullable=True)
    premarket_open = Column(Float, nullable=True)
    afterhours_close = Column(Float, nullable=True)
    options_maximum_pain = Column(Float, nullable=True)
    market_capitolization = Column(Float, nullable=True)
    fiftytwo_week_high = Column(Float, nullable=True)
    fiftytwo_week_low = Column(Float, nullable=True)
    #estimated_short_interest = Column(Float, nullable=True)
    #estimated_short_utilization = Column(Float, nullable=True)
    #short_cost_to_loan_min = Column(Float, nullable=True)
    #short_cost_to_loan_max = Column(Float, nullable=True)
    #short_cost_to_loan_ave = Column(Float, nullable=True)
    sentiment_reddit_mentions = Column(Integer, nullable=True)
    sentiment_reddit_bearish = Column(Float, nullable=True)
    sentiment_reddit_neutral = Column(Float, nullable=True)
    sentiment_reddit_bullish = Column(Float, nullable=True)
    sentiment_reddit_compound = Column(Float, nullable=True)

    #sentiment_google = Column(Float, nullable=True)
    #sentiment_congress = Column(Float, nullable=True)
    #sentiment_twitter = Column(Float, nullable=True)
    #sentiment_insider = Column(Float, nullable=True)
    #running_average_50day = Column(Float, nullable=True)
    #running_average_100day = Column(Float, nullable=True)
    #running_average_200day = Column(Float, nullable=True)

    def add_etf_daily(self, *args, **kwargs):
        daily_info = kwargs["yahoo"]
        ticker = kwargs["ticker"]
        daily_info.rename(columns={
            "Adj Close": "adjusted_close",
            "Stock Splits": "split"
        },
                          inplace=True)
        daily_info["Ticker"] = ticker
        print(daily_info)
        daily_info.to_sql("etf_daily", engine, if_exists="append")

        return None


class Etf1MinBars(Base):
    __tablename__ = "etf_1min_bars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(6), nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    fast_ema = Column(Float, nullable=True)
    slow_ema = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    market_open = Column(Boolean, nullable=True)


class Etf5MinBars(Base):
    __tablename__ = "etf_5min_bars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(6), nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    fast_ema = Column(Float, nullable=True)
    slow_ema = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    market_open = Column(Boolean, nullable=True)


class Etf15MinBars(Base):
    __tablename__ = "etf_15min_bars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(6), nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    fast_ema = Column(Float, nullable=True)
    slow_ema = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    market_open = Column(Boolean, nullable=True)


class Etf30MinBars(Base):
    __tablename__ = "etf_30min_bars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(6), nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    fast_ema = Column(Float, nullable=True)
    slow_ema = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    market_open = Column(Boolean, nullable=True)


class Etf1HrBars(Base):
    __tablename__ = "etf_1hour_bars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(6), nullable=False)
    datetime = Column(DateTime, nullable=False)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    adjusted_close = Column(Float, nullable=True)
    volume = Column(BigInteger, nullable=True)
    fast_ema = Column(Float, nullable=True)
    slow_ema = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    market_open = Column(Boolean, nullable=True)


def init_sqlalchemy():
    global engine
    conf = config.InvestingConfig()
    conf.read_config()
    database_url = conf.set_database_url()
    engine = create_engine(database_url)
    DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
