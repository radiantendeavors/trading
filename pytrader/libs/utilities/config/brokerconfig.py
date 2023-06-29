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
from pytrader import CLIENT_ID

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
        self.brokerclient_id = CLIENT_ID

    def read_config(self, *args, **kwargs):
        config = kwargs["config"]

        if "brokerclient_address" in config:
            self.brokerclient_address = config["brokerclient_address"]

    def get_brokerclient_address(self):
        return self.brokerclient_address

    def get_brokerclient_port(self):
        return self.brokerclient_port
