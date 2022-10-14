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
import os
import sys

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import argparse

# Other Application Libraries
from pytrader import *

# Conditional Libraries


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def nasdaq_download(args):
    print("Downloading data from NASDAQ")


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])

    cmd = subparsers.add_parser("nasdaq",
                                aliases=["n"],
                                parents=parent_parsers,
                                help="Downloads data from NASDAQ")
    cmd.add_argument("-e",
                     "--etfs",
                     action="store_true",
                     help="Download list of ETFs")
    cmd.add_argument("-s",
                     "--stocks",
                     action="store_true",
                     help="Download list of Stocks")

    cmd.set_defaults(func=nasdaq_download)

    return cmd
