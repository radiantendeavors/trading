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
import logging

# 3rd Party Libraries

# Application Libraries
# System Library Overrides

# Other Application Libraries

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
DEBUG = True

# Enable Logging
# create logger
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
