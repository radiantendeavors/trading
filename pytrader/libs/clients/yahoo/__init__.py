"""!@package pytrader.libs.clients.yahoo

Provides a client for gathering data from Yahoo! Finance

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

@file pytrader/libs/clients/yahoo/__init__.py

Provides a client for interfacing with Yahoo! Finance

Uses the yfinance library.
yFinance Documuentation: https://pypi.org/project/yfinance/

"""
# System Libraries
import requests_cache
from datetime import date

# 3rd Party Libraries
import yfinance

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients.mysql import etf_info, index_info, stock_info
from pytrader.libs.clients.mysql import etf_bar_daily_raw
from pytrader.libs.clients.mysql import index_bar_daily_raw
from pytrader.libs.clients.mysql import stock_bar_daily_raw

# Conditional Libraries

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
class YahooClient():

    def __init__(self):
        return None

    def get_ticker_list(self, info, check_symbol=1):
        if check_symbol:
            where = "`delisted_date` IS NULL and `ticker_symbol` IS NULL"
        else:
            where = "`delisted_date` IS NULL"

        return info.select(where_clause=where)

    def get_bar_history(self,
                        investment_type,
                        ticker,
                        yahoo_symbol,
                        interval="1d",
                        period="1mo"):

        session = requests_cache.CachedSession('yfinance.cache')
        session.headers[
            "User-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        # security = yfinance.Ticker(yahoo_symbol, session=session)
        # data = security.history(interval=interval, period=period)
        data = yfinance.download(yahoo_symbol,
                                 interval=interval,
                                 period=period)
        logger.debug("Data:\n%s", data)
        today = date.today()

        if investment_type == "stocks":
            history_table = stock_bar_daily_raw.StockBarDailyRaw()
        elif investment_type == "etfs":
            history_table = etf_bar_daily_raw.EtfBarDailyRaw()
        elif investment_type == "indexes":
            history_table = index_bar_daily_raw.IndexBarDailyRaw()

        logger.debug("Data Keys: %s", data.keys())
        logger.debug("Data Index: %s", data.index)

        for index, row in data.iterrows():
            logger.debug("Index: %s", index)
            history_table.insert(ticker, index, row["Open"], row["High"],
                                 row["Low"], row["Close"], row["Adj Close"],
                                 row["Volume"], "yahoo", today)

        return None

    def get_info(self, investment_type, ticker):
        logger.debug10("Begin Function")
        logger.debug("Ticker: %s", ticker)
        logger.debug2("Ticker[0]: %s", ticker[0])

        if "/" in ticker:
            yahoo_symbol = ticker.replace("/", "-")
        elif "^" in ticker and ticker[0] != "^":
            yahoo_symbol = ticker.replace("^", "-")
        else:
            yahoo_symbol = ticker

        logger.debug("Yahoo Symbol: %s", yahoo_symbol)

        session = requests_cache.CachedSession('yfinance.cache')
        session.headers[
            "User-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

        if investment_type == "stocks":
            info_table = stock_info.StockInfo()
        elif investment_type == "etfs":
            info_table = etf_info.EtfInfo()
        elif investment_type == "indexes":
            info_table = index_info.IndexInfo()

        try:
            security = yfinance.Ticker(yahoo_symbol, session=session)
            logger.debug("Security: %s", security)
            share_data = security.shares
            info_data = security.info

            logger.debug("Share Data: %s", share_data)
            logger.debug("Info Data: %s", info_data)

            if share_data is None and info_data is None:
                logger.error("No Share Data Found.  Data = %s", share_data)
                logger.error("No Info Data Found. Data = %s", info_data)
            else:
                info_table.update_yahoo_info(ticker, yahoo_symbol)
        except Exception as e:
            logger.error("Error updating yahoo data: %s", e)
            for index, row in share_data.iterrows():
                logger.debug2("Security: %s %s", index, row)

        logger.debug10("End Function")
        return security.info
