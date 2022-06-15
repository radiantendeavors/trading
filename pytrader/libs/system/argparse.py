#!/usr/bin/env python3
# ==================================================================================================# ==================================================================================================
#
# Original BASH version
# Original version Copyright 2001 by Kyle Sallee
# Additions/corrections Copyright 2002 by the Source Mage Team
#
# Python rewrite
# Copyright 2017 Geoff S Derber
#
# This file is part of Sorcery.
#
# File: pysorcery/lib/system/argparse.py
#
#    Sorcery is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published
#    by the Free Software Foundation, either version 3 of the License,
#    or (at your option) any later version.
#
#    Sorcery is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Sorcery.  If not, see <http://www.gnu.org/licenses/>.
#
# Argparse:
#
#    Provides additional functionality to the Argparse library from
#    Python.
#
# ==================================================================================================
"""
Argparse:

  Provides additional functionality to the Argparse library from
  Python.
"""

# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# System Libraries
from argparse import *

# 3rd Party Libraries

# Application Libraries
# System Library Overrides

# Other Application Libraries
from pytrader import __version__, DEBUG

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================

# ==================================================================================================
#
# Classes
#
# CommonParser
# ArgParser
#
# ==================================================================================================


# ==================================================================================================
#
# Class CommonParser
#
# Inputs
# ------
#    @param: *args    - tuple
#    @param: **kwargs - dictionary
#
# Returns
# -------
#    @param: None
#
# Raises
# ------
#    ...
#
# ==================================================================================================
class CommonParser(ArgumentParser):

    def __init__(self, *args, **kwargs):
        super(CommonParser, self).__init__(*args, **kwargs)
        return

    # ==============================================================================================
    #
    # Function create_subparsers
    #
    # Creates the subparser for the subcommands of the program.
    #
    # Inputs
    # ------
    #    @param: self -
    #
    # Returns
    # -------
    #    @return: self.subparser -
    #
    # Raises
    # ------
    #    ...
    #
    # ==============================================================================================
    def create_subparsers(self):
        self.subparser = self.add_subparsers(title='commands',
                                             metavar='Command',
                                             help='Description')
        return self.subparser

    # ==============================================================================================
    #
    # Function add_version_option
    #
    # Adds the argument '--version' which is common to all Sorcery
    # commands.
    #
    # Inputs
    # ------
    #    @param: self
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    # ==============================================================================================
    def add_version_option(self):
        self.add_argument('-V',
                          '--version',
                          action='version',
                          help='Print version information and exit',
                          version='%(prog)s ' + __version__)
        return None

    def add_ibapi_connection_options(self):
        self.add_argument(
            '-a',
            '--address',
            default="127.0.0.1",
            help="TWS / IB Gateway Address (Default is localhost)")
        self.add_argument('-p',
                          '--port',
                          default="7497",
                          type=int,
                          help="TWS / IB Gateway port (Default is 7497)")
        return None

    # ==============================================================================================
    #
    # Function read
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #
    # Returns
    # -------
    #    @return: self.parent
    #
    # Raises
    # ------
    #    ...
    #
    # ==============================================================================================
    def add_logging_option(self):
        # Common Help Descriptions:
        quiet_help = 'Decrease output'
        verbose_help = 'Increase output'
        loglevel_help = 'Specify output level'
        debug_help = 'Maximize output level'
        loglevel_choices = [
            'debug', 'info', 'warning', 'error', 'critical', 'DEBUG', 'INFO',
            'WARNING', 'ERROR', 'CRITICAL'
        ]

        # Create Parent Parsur
        self.parent = ArgumentParser(add_help=False)

        # Parser Groups
        # Logging Group
        self.logging = self.parent.add_argument_group('Logging Options')

        # Quiet Settings
        self.logging.add_argument('-q',
                                  '--quiet',
                                  action='count',
                                  default=0,
                                  help=quiet_help)
        # Verbose Options
        self.logging.add_argument('-v',
                                  '--verbosity',
                                  action='count',
                                  default=0,
                                  help=verbose_help)

        # If debugging is enabled
        if DEBUG:
            # Set Loglevel
            self.logging.add_argument('--loglevel',
                                      choices=loglevel_choices,
                                      default='INFO',
                                      help=loglevel_help)
            # Maximize logging
            self.logging.add_argument('--debug',
                                      action='store_true',
                                      help=debug_help)

        return self.parent


# ==================================================================================================
#
# Class ArgParser
#
# Inputs
# ------
#    @param: *args    - tuple of all subparsers and parent parsers
#                       args[0]: the subparser
#                       args[1:] the parent parsers


#
# Returns
# -------
#    @return: None
#
# Raises
# ------
#    ...
#
# ==================================================================================================
class ArgParser(CommonParser):
    pass
