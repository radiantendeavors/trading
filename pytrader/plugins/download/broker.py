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
import time
# import os
import sys

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients import broker
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


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def get_data_tickers(brokerclient, info, contract_id=1):
    if contract_id == 1:
        where = "`delisted_date` IS NULL AND `ibkr_symbol` IS NULL"
    else:
        where = "`delisted_date` IS NULL"
    return info.select(where_clause=where)


def get_ipo_tickers(brokerclient, info):
    where = "`delisted_date` IS NULL AND `ibkr_contract_id` IS NOT NULL"
    return info.select(where_clause=where)


def update_data_info(brokerclient, all_tickers, investments):
    logger.debug10("Begin Function")
    for item in all_tickers:
        logger.debug2("Item: %s", item)
        ticker = item["ticker"]
        if investments == "indexes":
            security_type = "IND"
        else:
            security_type = "STK"

        if item["ibkr_exchange"]:
            exchange = item["ibkr_exchange"]
        else:
            exchange = "SMART"

        logger.debug("Ticker: %s", ticker)
        logger.debug("Security Type: %s", security_type)
        logger.debug("Exchange: %s", exchange)

        if investments == "indexes":
            brokerclient.set_contract(ticker,
                                      security_type=security_type,
                                      exchange=exchange)
        else:
            brokerclient.set_contract(ticker)
        brokerclient.get_security_data()
        time.sleep(10)
    logger.debug10("End Function")
    return None


def update_ipo_info(brokerclient, all_tickers):
    logger.debug10("Begin Function")

    for item in all_tickers:
        ticker = item["ticker"]
        logger.debug("Ticker: %s", ticker)
        brokerclient.set_contract(ticker)
        ticker, req_id = brokerclient.get_ipo_date()
        logger.debug("Request ID: %s, Ticker: %s", req_id, ticker)
        time.sleep(10)

    logger.debug10("End Function")
    return None


def basic_info(investments, security=None):
    logger.debug("Begin Function")

    brokerclient = broker.BrokerClient()
    time.sleep(10)

    if investments == "indexes":
        info = index_info.IndexInfo()
    elif investments == "etfs":
        info = etf_info.EtfInfo()
    elif investments == "stocks":
        info = stock_info.StockInfo()
    else:
        logger.error("No investments were selected")
        sys.exit(1)

    for item in ["data", "ipo_date"]:
        if item == "data":
            if security:
                update_data_info(brokerclient, [security], investments)
            else:
                all_tickers = get_data_tickers(brokerclient, info)
                logger.debug("All tickers: %s", all_tickers)
                update_data_info(brokerclient, all_tickers, investments)
        if item == "ipo_date":
            if security:
                update_ipo_info(brokerclient, [security])
            else:
                all_tickers = get_ipo_tickers(brokerclient, info)
                update_ipo_info(brokerclient, all_tickers)

    logger.debug("End Function")


def broker_download(args):
    logging.debug("Begin Function")

    if args.type:
        investments = args.type
    else:
        investments = ["indexes", "etfs", "stocks"]

    if args.info:
        if args.security:
            basic_info("stocks", security=args.security)
        else:
            for investment in investments:
                basic_info(investment)

    return None


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])
    cmd = subparsers.add_parser("broker",
                                aliases=["b"],
                                parents=parent_parsers,
                                help="Downloads data from broker")
    cmd.add_argument("-b", "--bar-size", help="Bar Size")
    cmd.add_argument("-i",
                     "--info",
                     action="store_true",
                     help="Get Basic Security information.")
    cmd.add_argument("-s", "--security", help="Security to download")
    cmd.add_argument("-t",
                     "--type",
                     nargs=1,
                     choices=["etfs", "indexes", "stocks"],
                     help="Investment type to download information")
    cmd.set_defaults(func=broker_download)

    return cmd
