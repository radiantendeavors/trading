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
