#!/usr/bin/env python3
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import sys
import time

# 3rd Party libraries
from ibapi.client import Contract
from ibapi.order import Order

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader import DEBUG
from pytrader.libs import brokerclient

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Security():

    def __init__(self, client, ticker_symbol):
        self.ticker_symbol = ticker_symbol
        self.client = client

    def get_security_type(self):
        self.security_type = "STK"
        return self.security_type

    def get_security_currency(self):
        self.currency = "USD"
        return self.currency

    def set_security(self):
        self.client.set_contract(self.ticker_symbol)

    def get_security_data(self):
        self.client.get_security_data()
        time.sleep(60)

    def get_security_pricing_data(self):
        self.client.get_security_pricing_data()

    def get_option_chain(self, contract_id):
        logger.debug10("Get Option Chain")
        logger.debug("Ticker is: %s", self.ticker_symbol, contract_id)
        self.client.get_option_chain()

    def place_order(self,
                    action,
                    order_type,
                    order_price=None,
                    quantity=1.0,
                    time_in_force="DAY",
                    transmit=False):

        logger.info("Placing %s Order to %s %s of %s for %s %s", order_type,
                    action, quantity, self.ticker_symbol, order_price,
                    time_in_force)
        logger.debug("Transmit Order: %s", transmit)
        self.client.place_order(self.ticker_symbol, action, order_type,
                                order_price, quantity, time_in_force, transmit)
