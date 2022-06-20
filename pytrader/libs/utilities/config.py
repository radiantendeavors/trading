#! /usr/bin/env python3
#-----------------------------------------------------------------------
#
#
# Config:
#
#    Sets program configuration
#
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
#
# Libraries
#
#-----------------------------------------------------------------------

# System Libraries
import sys
import os
import yaml

# System Overrides
from pytrader.libs.system import logging
# Other Application Libraries

#-----------------------------------------------------------------------
#
# Global Variables
#
#-----------------------------------------------------------------------
# Enable Logging
# create logger
logger = logging.getLogger(__name__)
consolehandler = logging.ColorizingStreamHandler()

# home = os.path.expanduser("~") + "/"
# config_dir = home + ".config/investing"
# config_file = config_dir + "/config.yaml"
# config_stream = open(config_file)
# config = yaml.safe_load(config_stream)


class Config():

    def __init__(self, *args, **kwargs):
        self.database_type = "sqlite"
        self.database_driver = None
        self.database_username = None
        self.database_password = None
        self.database_host = "localhost"
        self.database_port = database_port[self.database_type]
        self.database_path = config_dir
        self.database_name = "investing"
        self.reddit_user_agent = None
        self.reddit_client_id = None
        self.reddit_client_secret = None
        self.reddit_username = None
        self.reddit_password = None
        self.nasdaq_client_key = None
        self.nasdaq_client_secret = None
        return None

    def read_config(self, *args, **kwargs):
        if "database_type" in config:
            self.database_type = config["database_type"]
            self.database_port = database_port[self.database_type]

        if "database_driver" in config:
            self.database_driver = config["database_driver"]
        elif self.database_type == "sqlite":
            self.database_driver = "pysqlite"
        else:
            self.database_driver = None

        if "database_username" in config:
            self.database_username = config["database_username"]

        if "database_password" in config:
            self.database_password = config["database_password"]

        if "database_path" in config:
            self.database_path = config["database_path"]

        if "database_name" in config:
            self.database_name = config["database_name"]

        if "database_host" in config:
            self.database_host = config["database_host"]

    def set_database_url(self, *args, **kwargs):
        url = self.database_type

        if self.database_driver is not None:
            url = url + "+" + self.database_driver + "://"
        else:
            url = url + "://"

        if self.database_type == "sqlite":
            if self.database_name != "memory":
                url = url + "/" + self.database_path
                url = url + "/" + self.database_name
                url = url + ".db"
        else:
            if self.database_username is not None:
                if self.database_password is not None:
                    url = url + self.database_username + ":" + self.database_password
                else:
                    url = url + self.database_username

            url = url + "@" + self.database_host
            url = url + ":" + self.database_port
            url = url + "/" + self.database_name

        self.database_url = url
        return url


#-----------------------------------------------------------------------
#
# configure_logging
#
# Configure the logger.
#
# Inputs
# ------
#    @param: args
#    @param: config
#
# Returns
# -------
#    @return: None
#
# Raises
# ------
#    ...
#
#-----------------------------------------------------------------------
def configure_logging(args, config):
    global logger
    global consolhandler

    logger.debug("Begin Function")

    # Ugly hack to make the changes global
    tempname = __name__.split(":")[0].split(".")[0]
    logger = logging.getLogger(tempname)

    loglevels = {
        'debug': 10,
        'info': 20,
        'warning': 30,
        'error': 40,
        'critical': 50
    }

    if config['logging']['verbosity'] == 0:
        config['logging']['loglevel'] = loglevels[config['logging']
                                                  ['loglevel']]
    else:
        config['logging']['loglevel'] = 20 - min(
            20, config['logging']['verbosity'])

    if args.debug:
        config['logging']['loglevel'] = 1
    elif args.quiet > 0:
        config['logging']['loglevel'] = 20 + args.quiet
    elif args.verbosity > 0:
        config['logging']['loglevel'] = 20 - args.verbosity
    else:
        # Bind loglevel to the upper case string value obtained
        # from the command line argument.  This allows the user to
        # specify --log=DEBUG or --log=debug
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % args.loglevel)
        config['logging']['loglevel'] = numeric_level

    logger.setLevel(config['logging']['loglevel'])
    consolehandler.setLevel(config['logging']['loglevel'])

    # End ugly hack to change logging level globally
    logger = logging.getLogger(__name__)

    # If debugging enabled, log the arguments passed to the program
    logger.debug(logger)
    logger.debug("Arguments Processed")
    #    logger.debug2("Arguments: " + str(args))

    logger.debug("End Function")
    return None


#-----------------------------------------------------------------------
#
# defConfiguration
#
# Gather the default plugins
#
# Inputs
# ------
#    ...
#
# Returns
# -------
#    none
#
# Raises
# ------
#    ...
#
#-----------------------------------------------------------------------
def defConfiguration():
    logging_config = {"loglevel": "info", "verbosity": 0}

    config = {
        'logging': logging_config,
    }
    return config


#-----------------------------------------------------------------------
#
# configure
#
# Load configuration settings in the following order:
# 1. Hard Coded
# 2. {python-dir}/dist-___/pydionysius/dionysius_default.conf
# 3. ~/.config/dionysius/dionysis.conf
# 4. cli switches
#
# As each configuartion is loaded, it will overwrite any previosly set
# configuration option.
#
# Inputs
# ------
#    ...
#
# Returns
# -------
#    none
#
# Raises
# ------
#    ...
#
#-----------------------------------------------------------------------
def main_configure(args):
    logger.debug("Begin Function")

    # Default Settings
    config = defConfiguration()

    # Congigure Loggings
    configure_logging(args, config)

    logger.debug2("Return variable: Config:\n" + str(config))
    logger.debug("End Function")
    return config


def main(*args, **kwargs):
    config = Config()
    config.read_config()
    config.print_config()


if __name__ == "__main__":
    main()
