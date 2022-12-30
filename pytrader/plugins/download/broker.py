"""!@package pytrader.plugins.download.broker

The Broker SubCommand for pytrdownload

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


"""

# System Libraries
# import os
import sys

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import indexes
from pytrader.libs.clients import broker
from pytrader.libs.securities import etfs, stocks
from pytrader.libs.utilities import config
from pytrader.ui.pytrdownload import client_id

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
def basic_info(investments, brokerclient, security=None):
    """
    basic_info

    @param investments
    @param brokerclient
    @param security
    """
    logger.debug("Begin Function")

    if investments == "indexes":
        info = indexes.Indexes(brokerclient=brokerclient)
    elif investments == "etfs":
        info = etfs.Etfs(brokerclient=brokerclient)
    elif investments == "stocks":
        info = stocks.Stocks(brokerclient=brokerclient)
    else:
        logger.error("No investments were selected")
        sys.exit(1)

    info.update_info("broker")
    logger.debug("End Function")


def broker_download(args):
    """
    broker_download

    @param args
    """
    logging.debug("Begin Function")
    conf = config.Config()
    conf.read_config()

    if args.address:
        address = args.address
    else:
        address = conf.brokerclient_address

    if args.port:
        port = args.port
    else:
        port = conf.brokerclient_port

    brokerclient = broker.broker_connect(address, port, client_id=client_id)

    if args.type:
        investments = args.type
    else:
        investments = ["indexes", "etfs", "stocks"]

    if args.info:
        if args.security:
            basic_info("stocks", brokerclient, security=args.security)
        else:
            for investment in investments:
                basic_info(investment, brokerclient)

    brokerclient.disconnect()
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
