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
def get_data_tickers(brokerclient, info):
    where = "`delisted_date` IS NULL"
    return info.select_all_tickers(where=where)


def get_ipo_tickers(brokerclient, info):
    where = "`delisted_date` IS NULL AND `ibkr_contract_id` IS NOT NULL"
    return info.select_all_tickers(where=where)


def update_data_info(brokerclient, all_tickers):
    for item in all_tickers:
        ticker = item["ticker"]
        logger.debug("Ticker: %s", ticker)
        brokerclient.set_contract(ticker)
        brokerclient.get_security_data()
        time.sleep(10)


def update_ipo_info(brokerclient, all_tickers):
    for item in all_tickers:
        ticker = item["ticker"]
        logger.debug("Ticker: %s", ticker)
        brokerclient.set_contract(ticker)
        ticker, req_id = brokerclient.get_ipo_date()
        logger.debug("Request ID: %s, Ticker: %s", req_id, ticker)
        time.sleep(10)


def client(investments):
    logger.debug("Begin Function")

    brokerclient = broker.BrokerClient()
    time.sleep(10)

    if investments == "etf":
        info = etf_info.EtfInfo()
    elif investments == "stocks":
        info = stock_info.StockInfo()
    else:
        logger.error("No investments were selected")
        sys.exit(1)

    for item in ["data", "ipo_date"]:
        if item == "data":
            all_tickers = get_data_tickers(brokerclient, info)
            update_data_info(brokerclient, all_tickers)
        if item == "ipo_date":
            all_tickers = get_ipo_tickers(brokerclient, info)
            update_ipo_info(brokerclient, all_tickers)

    logger.debug("End Function")


def broker_download(args):
    logging.debug("Begin Function")

    investments = ["etf"]
    for investment in investments:
        client(investment)

    return None


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])
    cmd = subparsers.add_parser("broker",
                                aliases=["b"],
                                parents=parent_parsers,
                                help="Downloads historical data from broker")
    cmd.add_argument("-b", "--bar-size", help="Bar Size")
    cmd.add_argument("-s", "--security", help="Security to download")

    cmd.set_defaults(func=broker_download)

    return cmd
