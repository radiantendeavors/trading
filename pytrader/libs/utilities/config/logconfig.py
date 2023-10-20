"""!@package pytrader.libs.utilities.config.logconfig

Reads the config files.

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


@file pytrader/libs/utilities/config/__init__.py
"""
import argparse

from pytrader import LOGLEVEL, consolehandler, logger
from pytrader.libs.system import logging


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class LogConfig():
    """!
    Class for parsing logging related settings.
    """

    loglevel = LOGLEVEL

    def read_config(self, *args, **kwargs) -> None:
        """!
        Parses the config for logging related settings.

        @param *args:
        @param **kwargs:

        @return None
        """
        config = kwargs["config"]

        loglevels = {'debug': 10, 'info': 20, 'warning': 30, 'error': 40, 'critical': 50}

        if "logging" in config:
            if "loglevel" in config["logging"]:
                self.loglevel = loglevels[config["logging"]["loglevel"]]
            if "verbosity" in config["logging"]:
                self.loglevel = 11 - min(10, config["logging"]["verbosity"])

    def update_loglevel(self, args: argparse.Namespace) -> None:
        """!
        Updates the desired loglevel

        @param args:

        @return None
        """
        if args.debug:
            self.loglevel = 1
        elif args.quiet > 0:
            self.loglevel = 20 + args.quiet
        elif args.verbosity > 0:
            self.loglevel = 11 - args.verbosity
        else:
            # Bind loglevel to the upper case string value obtained
            # from the command line argument.  This allows the user to
            # specify --log=DEBUG or --log=debug
            numeric_level = getattr(logging, args.loglevel.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError(f"Invalid log level: {args.loglevel}")
            self.loglevel = numeric_level

    def set_loglevel(self, args: argparse.Namespace) -> None:
        """!
        Sets the loglevel

        @param args:

        @return None
        """
        self.update_loglevel(args)
        logger.setLevel(self.loglevel)
        consolehandler.setLevel(self.loglevel)

        # If debugging enabled, log the arguments passed to the program
        logger.debug(logger)
        logger.debug("Arguments Processed")

        logger.debug10("End Function")
