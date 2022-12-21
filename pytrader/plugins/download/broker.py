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
# import os
# import sys

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
# from pytrader.libs.system import argparse

# Other Application Libraries
# from pytrader import *

# Conditional Libraries


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def broker_download(args):
    print("Downloading data from broker")


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
