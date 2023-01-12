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

@file plugins/download/nasdaq.py

    Contains global variables for the pyTrader program.

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

    investments = "None"

    if args.type:
        investments = args.type
    else:
        investments = ["etfs", "indexes", "stocks"]

    for investment in investments:
        if args.security:
            info = securities.Securities(securities_type=investment,
                                         securities_list=args.security)
        else:
            info = securities.Securities(securities_type=investment)

        info.update_info(source="polygon")

    logging.debug("End Fuction")
    return None


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])

    cmd = subparsers.add_parser("polygon",
                                aliases=["p"],
                                parents=parent_parsers,
                                help="Downloads data from Polygon.IO")
    cmd.add_argument("-s",
                     "--security",
                     nargs="+",
                     help="Security to download")
    cmd.add_argument("-t",
                     "--type",
                     nargs=1,
                     choices=["etfs", "indexes", "stocks"],
                     help="Type of investments to download")

    cmd.set_defaults(func=polygon_download)

    return cmd
