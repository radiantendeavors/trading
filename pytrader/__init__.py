#!/usr/bin/env python3

# ==================================================================================================
#
# Dunders
#
# ==================================================================================================
__all__ = [
    '__author__', '__contact__', '__copyright__', '__license__', '__status__',
    '__version__', 'DEBUG'
]

__author__ = 'G S Derber'
__contact__ = 'gd.github@radiantendeavors.com'
__copyright__ = 2022
__license__ = 'AGPL'
__status__ = 'Prototype'
__version__ = 'HEAD'

# ==================================================================================================
#
# Libraries
#
# ==================================================================================================
# System Libraries

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging
# Other Application Libraries

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
DEBUG = True
LOGLEVEL = 0

# Enable Logging
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(LOGLEVEL)

consolehandler = logging.ColorizingStreamHandler()

# Define Formatters
consoleformatter = logging.ConsoleLvlFormatter(
    "%(name)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s")

# Set handler ...
consolehandler.setLevel(LOGLEVEL)
consolehandler.setFormatter(consoleformatter)

# Add handlers to logger
logger.addHandler(consolehandler)
