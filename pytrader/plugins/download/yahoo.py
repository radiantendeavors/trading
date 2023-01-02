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

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import securities

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


def yahoo_download(args):
    logger.debug10("Begin Function")

    if args.security:
        logger.debug("Get information and history for individual security")
    else:
        if args.type:
            investments = args.type
        else:
            investments = ["indexes", "etfs", "stocks"]

        for investment in investments:
            info = securities.Securities(securities_type=investment)

            if args.info:
                info.update_info(source="yahoo")
            elif args.history:
                info.update_history("yahoo", args.bar_size, args.period)
            else:
                info.update_info(source="yahoo")
                info.update_history("yahoo", args.bar_size, args.period)

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
    cmd.add_argument("-H",
                     "--history",
                     action="store_true",
                     help="Get Price history.")
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
    cmd.set_defaults(func=yahoo_download)

    return cmd
