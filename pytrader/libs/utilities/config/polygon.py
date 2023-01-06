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
# Enable Logging
# create logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class PolygonConfig():

    def __init__(self, *args, **kwargs):
        self.polygon_api_key = ""

    def read_config(self, *args, **kwargs):
        config = kwargs["config"]

        if "polygon_api_key" in config:
            self.polygon_api_key = config["polygon_api_key"]

    def get_polygon_api_key(self):
        return self.polygon_api_key
