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
