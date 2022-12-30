#! /usr/bin/env python3
# ==================================================================================================
#
#
# Config:
#
#    Sets program configuration
#
# ==================================================================================================

# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# System Libraries

# System Overrides
from pytrader.libs.system import logging
# Other Application Libraries
from pytrader import logger, LOGLEVEL, consolehandler

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.
"""


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class LogConfig():

    def __init__(self, *args, **kwargs):
        self.loglevel = LOGLEVEL
        return None

    def read_config(self, *args, **kwargs):
        config = kwargs["config"]

        loglevels = {
            'debug': 10,
            'info': 20,
            'warning': 30,
            'error': 40,
            'critical': 50
        }

        if "logging" in config:
            if "loglevel" in config["logging"]:
                self.loglevel = loglevels[config["logging"]["loglevel"]]
            if "verbosity" in config["logging"]:
                self.loglevel = 11 - min(10, config["logging"]["verbosity"])
        return None

    def update_loglevel(self, args):
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
                raise ValueError('Invalid log level: %s' % args.loglevel)
            self.loglevel = numeric_level
        return None

    def set_loglevel(self, args):
        self.update_loglevel(args)
        logger.setLevel(self.loglevel)
        consolehandler.setLevel(self.loglevel)

        # If debugging enabled, log the arguments passed to the program
        logger.debug(logger)
        logger.debug("Arguments Processed")

        logger.debug10("End Function")
        return None
