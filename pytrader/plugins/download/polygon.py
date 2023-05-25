"""!@package pytrader.plugins.download.polygon

Downloads External Data from Polygon.io

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

@file pytrader/plugins/download/polygon.py

Downloads External Data from Polygon.io

"""

# System Libraries
# import os
# import sys

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
# from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import contracts
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
# Functions
#
# ==================================================================================================
def polygon_download(args):
    logging.debug("Begin Function")

    if args.securities:
        securities = args.securities
    else:
        securities = None

    contracts_ = contracts.Contracts(securities)
    contracts_.update_info("polygon", args.asset_class, args.locale)

    logging.debug("End Fuction")
    return None


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])

    cmd = subparsers.add_parser("polygon",
                                aliases=["p"],
                                parents=parent_parsers,
                                help="Downloads data from Polygon.IO")
    cmd.add_argument("-a",
                     "--asset_class",
                     nargs="+",
                     choices=["stocks", "options", "crypto", "fx", "indices"],
                     default=["stocks", "indices"],
                     help="Type of investments to download")
    cmd.add_argument("-l",
                     "--locale",
                     nargs="?",
                     choices=["us", "global"],
                     default="us",
                     help="Locale for securities")
    cmd.add_argument("-s",
                     "--securities",
                     nargs="*",
                     help="Securities to download")

    cmd.set_defaults(func=polygon_download)

    return cmd
