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

@file plugins/download/broker.py

    Contains global variables for the pyTrader program.

"""

# System Libraries
import random
import sys
import time

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients import yahoo
from pytrader.libs.clients.mysql import etf_info
from pytrader.libs.clients.mysql import index_info
from pytrader.libs.clients.mysql import stock_info
from pytrader.libs.utilities import config

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

"""
logger = logging.getLogger(__name__)

min_sleeptime = 61
max_sleeptime = 121


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def history(investments, args):
    if investments == "indexes":
        info = index_info.IndexInfo()
    elif investments == "etfs":
        info = etf_info.EtfInfo()
    elif investments == "stocks":
        info = stock_info.StockInfo()
    else:
        logger.error("No investments were selected")
        sys.exit(1)

    yc = yahoo.YahooClient()
    all_tickers = yc.get_ticker_list(info)

    for ticker in all_tickers:
        logger.debug("Ticker: %s", ticker["yahoo_symbol"])
        if ticker["yahoo_symbol"]:
            yahoo_symbol = ticker["yahoo_symbol"]
        else:
            yahoo_symbol = ticker["ticker"]

        yc.get_bar_history(info,
                           ticker["ticker"],
                           yahoo_symbol,
                           interval=args.bar_size,
                           period=args.period)
        time.sleep(random.randint(min_sleeptime, max_sleeptime))


def information(investments, args):
    logger.debug10("Begin Function")
    if investments == "indexes":
        info_table = index_info.IndexInfo()
    elif investments == "etfs":
        info_table = etf_info.EtfInfo()
    elif investments == "stocks":
        info_table = stock_info.StockInfo()
    else:
        logger.error("No investments were selected")
        sys.exit(1)

    yc = yahoo.YahooClient()

    if args.security:
        info = yc.get_info(args.security, info_table)
        logger.debug("Info: ", info)
    else:
        all_tickers = yc.get_ticker_list(info_table, check_symbol=0)
        for ticker in all_tickers:
            logger.debug("Ticker: %s", ticker["yahoo_symbol"])
            if ticker["yahoo_symbol"]:
                yahoo_symbol = ticker["yahoo_symbol"]
            else:
                yahoo_symbol = ticker["ticker"]
                info = yc.get_info(yahoo_symbol, info_table)
                logger.debug("Info: ", info)
                #time.sleep(random.randint(min_sleeptime, max_sleeptime))

    logger.debug10("End Function")
    return None


def broker_download(args):
    logger.debug10("Begin Function")

    if args.type:
        investments = args.type
    else:
        investments = ["indexes", "etfs", "stocks"]

    for investment in investments:
        information(investment, args)
        history(investment, args)

    logger.debug10("End Function")

    return None


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])
    cmd = subparsers.add_parser("yahoo",
                                aliases=["y"],
                                parents=parent_parsers,
                                help="Downloads data from broker")
    cmd.add_argument("-b",
                     "--bar-size",
                     nargs=1,
                     choices=[
                         "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h",
                         "1d", "5d", "1wk", "1mo", "3mo"
                     ],
                     default="1d",
                     help="Bar Size  (Default: '1d')")
    cmd.add_argument("-i",
                     "--info",
                     action="store_true",
                     help="Get Basic Security information.")
    cmd.add_argument("-p",
                     "--period",
                     nargs=1,
                     choices=[
                         "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y",
                         "10y", "ytd", "max"
                     ],
                     default="1mo",
                     help="How long of history to download (Default: '1mo')")
    cmd.add_argument("-s", "--security", help="Security to download")
    cmd.add_argument("-t",
                     "--type",
                     nargs=1,
                     choices=["etfs", "stocks", "indexes"],
                     help="Investment type to download information")
    cmd.set_defaults(func=broker_download)

    return cmd
