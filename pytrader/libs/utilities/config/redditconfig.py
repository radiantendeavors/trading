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

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class RedditConfig():

    def __init__(self, *args, **kwargs):
        self.reddit_user_agent = None
        self.reddit_client_id = None
        self.reddit_client_secret = None
        self.reddit_username = None
        self.reddit_password = None
