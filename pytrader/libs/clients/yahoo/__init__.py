"""!@package pytrader

Algorithmic Trading Program

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

@file lib/nasdaqclient/__init__.py

    Contains global variables for the pyTrader program.

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
from pytrader.libs.clients.mysql import index_bar_daily_raw

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
            where = "`delisted_date` IS NULL AND yahoo_symbol IS NOT NULL"
        else:
            where = "`delisted_date` IS NULL"

        return info.select(where_clause=where)

    def get_bar_history(self,
                        history,
                        ticker,
                        yahoo_symbol,
                        interval="1d",
                        period="1mo"):

        session = requests_cache.CachedSession('yfinance.cache')
        session.headers[
            "User-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        security = yfinance.Ticker(yahoo_symbol, session=session)
        #data = security.history(interval=interval, period=period)
        data = yfinance.download(yahoo_symbol,
                                 interval=interval,
                                 period=period)
        logger.debug("Data:\n%s", data)
        today = date.today()
        history = index_bar_daily_raw.IndexBarDailyRaw()

        logger.debug("Data Keys: %s", data.keys())
        logger.debug("Data Index: %s", data.index)

        for index, row in data.iterrows():
            logger.debug("Index: %s", index)
            history.insert(ticker, index, row["Open"], row["High"], row["Low"],
                           row["Close"], row["Adj Close"], row["Volume"],
                           "yahoo", today)

        return None

    def get_info(self, ticker, info_table=None):
        logger.debug10("Begin Function")
        logger.debug("Ticker: %s", ticker)

        if "/" in ticker:
            yahoo_symbol = ticker.replace("/", "-")
        else:
            yahoo_symbol = ticker

        logger.debug("Yahoo Symbol: %s", yahoo_symbol)

        session = requests_cache.CachedSession('yfinance.cache')
        session.headers[
            "User-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

        try:
            security = yfinance.Ticker(yahoo_symbol, session=session)
            data = security.shares
            if info_table:
                info_table.update_yahoo_info(ticker, yahoo_symbol)
        except Exception as e:
            logger.error("Error updating yahoo data: %s", e)
            for index, row in data.iterrows():
                logger.debug2("Security: %s %s", index, row)

        logger.debug10("End Function")
        return security.info
