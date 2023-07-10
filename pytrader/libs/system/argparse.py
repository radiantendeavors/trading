"""!@package pytrader.libs.system.argparse

Provides additional functionality to the Argparse library from Python.

@author G. S. Derber
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

@file pytrader/libs/system/argparse.py
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
from pytrader.libs.utilities import config

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
class CommonParser(ArgumentParser):
    """
    class CommonParser

    @param *args: tbd
    @param **kwargs: tbd

    @return None
    """

    def __init__(self, *args, **kwargs):
        super(CommonParser, self).__init__(*args, **kwargs)

    # ==============================================================================================
    #
    # Function create_subparsers
    #
    #
    # Raises
    # ------
    #    ...
    #
    # ==============================================================================================
    def create_subparsers(self):
        """!
        Creates the subparser for the subcommands of the program.

        @param: self

        @return: self.subparser: tbd
        """
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

    # ==============================================================================================
    #
    # Function add_ibapi_connection_options
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
    #
    # Defaults Ports:
    #         | Live | Demo |
    # --------+------+------|
    # TWS     | 7496 | 7497 |
    # Gateway | 4001 | 4002 |
    #
    # ==============================================================================================
    def add_ibapi_connection_options(self):
        conf = config.Config()

        default_address = conf.get_brokerclient_address()
        self.add_argument('-a',
                          '--address',
                          default=default_address,
                          help="TWS / IB Gateway Address (Default is localhost)")
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
            'debug', 'info', 'warning', 'error', 'critical', 'DEBUG', 'INFO', 'WARNING', 'ERROR',
            'CRITICAL'
        ]

        # Create Parent Parser
        self.parent = ArgumentParser(add_help=False)

        # Parser Groups
        # Logging Group
        # self.parent_logging = self.parent.add_argument_group("Logging Options")
        self.logging = self.add_argument_group('Logging Options')

        # Quiet Settings
        self.logging.add_argument('-q', '--quiet', action='count', default=0, help=quiet_help)
        # self.parent_logging.add_argument('-q',
        #                                  '--quiet',
        #                                  action='count',
        #                                  default=0,
        #                                  help=quiet_help)

        # Verbose Options
        self.logging.add_argument('-v', '--verbosity', action='count', default=0, help=verbose_help)

        # self.parent_logging.add_argument('-v',
        #                                  '--verbosity',
        #                                  action='count',
        #                                  default=0,
        #                                  help=verbose_help)

        # If debugging is enabled
        if DEBUG:
            # Set Loglevel
            self.logging.add_argument('--loglevel',
                                      choices=loglevel_choices,
                                      default='INFO',
                                      help=loglevel_help)
            # Maximize logging
            self.logging.add_argument('--debug', action='store_true', help=debug_help)

            # # Set Loglevel
            # self.parent_logging.add_argument('--loglevel',
            #                                  choices=loglevel_choices,
            #                                  default='INFO',
            #                                  help=loglevel_help)
            # # Maximize logging
            # self.parent_logging.add_argument('--debug',
            #                                  action='store_true',
            #                                  help=debug_help)

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
