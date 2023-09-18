"""!@package pytrader.libs.system.argparse

Provides a wrapper arround pythons argparse library, with additional functionality.

@author G S Derber
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
# This file requires special pylint rules to match the API format.
#
# W0611: Unused import (ArgumentError)
#
# pylint: disable=W0611
#
# ==================================================================================================
# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# System Libraries
from argparse import ArgumentParser, ArgumentError

# 3rd Party Libraries

# Application Libraries
# System Library Overrides

# Other Application Libraries
from pytrader import __version__, DEBUG, CLIENT_ID
from pytrader.libs.utilities.config.broker import BROKERS

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
class ArgParser(ArgumentParser):
    """!
    Adds default options for all pytrader commands
    """

    def __init__(self, *args, **kwargs) -> None:
        """!
        Initializes ArgParser

        @return None
        """
        super().__init__(*args, **kwargs)
        self.subparser = None
        self.parent = None
        self.logging = None

    def create_subparsers(self):
        """!
        Creates the subparser for the subcommands of the program.

        @return: self.subparser: tbd
        """
        self.subparser = self.add_subparsers(title="commands",
                                             metavar="Command",
                                             help="Description")

        return self.subparser

    def add_version_option(self) -> None:
        """!
        Adds the argument '--version' which is common to all commands.

        @return None
        """
        self.add_argument("-V",
                          "--version",
                          action='version',
                          help='Print version information and exit',
                          version='%(prog)s ' + __version__)

    def add_broker_options(self) -> None:
        """!
        Adds options related to the broker.

        @return None
        """
        broker_list = list(BROKERS)
        help_str = (f"Brokers (Default: {broker_list})\n"
                    f"If 'backtest' is chosen, all other brokers will be ignored.")
        broker = self.add_argument_group("broker")
        broker.add_argument("-b",
                            "--broker",
                            nargs="*",
                            choices=broker_list,
                            default=[broker_list[0]],
                            help=help_str)
        broker.add_argument("-c",
                            "--client-id",
                            default=CLIENT_ID,
                            help=f"Broker Client Id (Default: {CLIENT_ID})")
        default_address = "127.0.0.1"
        broker.add_argument("-a",
                            "--address",
                            default=default_address,
                            help=f"The Broker Address (Default: {default_address})")
        broker.add_argument("-d",
                            "--disable-broker",
                            action="store_false",
                            default=True,
                            help="Disable Broker Initialization")
        broker.add_argument("-p",
                            "--ports",
                            nargs="*",
                            metavar="PORT",
                            help="List of ports available to connect to.")

    def add_logging_option(self):
        """!
        Adds logging options.

        @return self.parent
        """
        # Common Help Descriptions:
        quiet_help = "Decrease output"
        verbose_help = "Increase output"
        loglevel_help = "Specify output level"
        debug_help = "Maximize output level"
        loglevel_choices = [
            "debug", "info", "warning", "error", "critical", "DEBUG", "INFO", "WARNING", "ERROR",
            "CRITICAL"
        ]

        # Create Parent Parser
        self.parent = ArgumentParser(add_help=False)

        # Parser Groups
        # Logging Group
        # self.parent_logging = self.parent.add_argument_group("Logging Options")
        self.logging = self.add_argument_group("Logging Options")

        # Quiet Settings
        self.logging.add_argument("-q", "--quiet", action="count", default=0, help=quiet_help)
        # self.parent_logging.add_argument("-q",
        #                                  "--quiet",
        #                                  action="count",
        #                                  default=0,
        #                                  help=quiet_help)

        # Verbose Options
        self.logging.add_argument("-v", "--verbosity", action="count", default=0, help=verbose_help)

        # self.parent_logging.add_argument("-v",
        #                                  "--verbosity",
        #                                  action="count",
        #                                  default=0,
        #                                  help=verbose_help)

        # If debugging is enabled
        if DEBUG:
            # Set Loglevel
            self.logging.add_argument("--loglevel",
                                      choices=loglevel_choices,
                                      default="INFO",
                                      help=loglevel_help)
            # Maximize logging
            self.logging.add_argument("--debug", action="store_true", help=debug_help)

            # # Set Loglevel
            # self.parent_logging.add_argument("--loglevel",
            #                                  choices=loglevel_choices,
            #                                  default="INFO",
            #                                  help=loglevel_help)
            # # Maximize logging
            # self.parent_logging.add_argument("--debug",
            #                                  action="store_true",
            #                                  help=debug_help)

        return self.parent
