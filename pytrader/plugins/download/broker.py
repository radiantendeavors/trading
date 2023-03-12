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
from pytrader.libs import securities
from pytrader.libs.applications import downloader
from pytrader.libs.clients import broker
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


def broker_download(args):
    """!
    broker_download

    @param args
    """
    logger.debug10("Begin Function")
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

    brokerclient = broker.brokerclient("ibkr")
    brokerclient.connect(address, port, client_id)
    brokerclient.start_thread()

    if args.type:
        investments = args.type
    else:
        investments = ["indexes", "etfs", "stocks"]

    dl = downloader.DownloadProcess()

    if args.info:
        if args.security:
            dl.download_info(investments[0],
                             brokerclient,
                             securities_list=args.security)
        else:
            for investment in investments:
                dl.download_info(investment, brokerclient)

    if args.bar_size:
        if args.security:
            dl.download_bars(investments[0], brokerclient, args.bar_size,
                             args.security, args.duration)

    brokerclient.disconnect()
    logger.debug10("End Function")
    return None


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])
    cmd = subparsers.add_parser("broker",
                                aliases=["b"],
                                parents=parent_parsers,
                                help="Downloads data from broker")
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
    cmd.add_argument("-i",
                     "--info",
                     action="store_true",
                     help="Get Basic Security information.")
    cmd.add_argument("-d", "--duration", help="How far back to get data")
    cmd.add_argument("-s",
                     "--security",
                     nargs="+",
                     help="Security to download")
    cmd.add_argument("-t",
                     "--type",
                     nargs=1,
                     choices=["etfs", "indexes", "stocks"],
                     help="Investment type to download information")
    cmd.set_defaults(func=broker_download)

    return cmd
