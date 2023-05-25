"""!@package pytrader.plugins.download.broker

The Broker SubCommand for pytrdownload

@author Geoff S. Derber
@version HEAD
@date 2022-2023
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

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import contracts
from pytrader.libs.applications import downloader
from pytrader.libs.applications import trader
from pytrader.libs.clients import broker
from pytrader.libs.utilities import config
from pytrader.ui.pytrdownload import client_id

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def broker_address(args, conf):
    """!
    Returns the address to be used by the broker.

    @param args - Provides the arguments from the command line
    @param conf - Provides the configuration information from config files.

    @return address - The brokeclient's address
    """
    if args.address:
        return args.address
    else:
        return conf.brokerclient_address


def broker_download(args):
    """!
    broker_download

    @param args
    """
    logger.debug10("Begin Function")
    conf = config.Config()
    conf.read_config()

    address = broker_address(args, conf)

    process_manager = trader.ProcessManager()
    process_manager.run_processes(address,
                                  securities_list=args.securities,
                                  asset_classes=args.asset_class)


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])
    cmd = subparsers.add_parser("broker",
                                aliases=["b"],
                                parents=parent_parsers,
                                help="Downloads data from broker")
    cmd.add_argument("-a",
                     "--asset_class",
                     nargs="+",
                     choices=[
                         "stocks", "options", "futures", "futures_options",
                         "forex", "combo", "warrant", "bond", "commodity",
                         "news", "fund", "crypto", "indices"
                     ],
                     default=["stocks", "indices"],
                     help="Type of investments to download")
    cmd.add_argument("-b",
                     "--bar-size",
                     choices=[
                         "1secs", "5secs", "10secs", "15secs", "30secs",
                         "1min", "2mins", "3mins", "5mins", "10mins", "15mins",
                         "20mins", "30mins", "1hour", "2hours", "3hours",
                         "4hours", "8hours", "1day", "1week", "1month"
                     ],
                     nargs="+",
                     help="Bar Size")
    cmd.add_argument("-d", "--duration", help="How far back to get data")
    cmd.add_argument("-i",
                     "--info",
                     action="store_true",
                     help="Get Basic Security information.")
    cmd.add_argument("-s",
                     "--securities",
                     nargs="*",
                     help="Securities to download")
    cmd.set_defaults(func=broker_download)

    return cmd
