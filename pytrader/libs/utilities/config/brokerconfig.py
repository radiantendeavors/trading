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
class BrokerConfig():

    def __init__(self, *args, **kwargs):
        self.brokerclient_address = "127.0.0.1"
        self.brokerclient_id = 2004

    def read_config(self, *args, **kwargs):
        config = kwargs["config"]

        if "brokerclient_address" in config:
            self.brokerclient_address = config["brokerclient_address"]

        if "brokerclient_id" in config:
            self.brokerclient_id = config["brokerclient_id"]

    def get_brokerclient_address(self):
        return self.brokerclient_address

    def get_brokerclient_id(self):
        return self.brokerclient_id
