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
def initial_download(args):
    print("Downloading data from broker")


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])

    cmd = subparsers.add_parser("init",
                                aliases=["i"],
                                parents=parent_parsers,
                                help="Initial data download")

    cmd.set_defaults(func=initial_download)

    return cmd
