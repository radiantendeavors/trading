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

    def __init__(self, ticker_symbol):
        self.ticker_symbol = ticker_symbol

    def get_security_type(self):
        self.security_type = "STK"
        return self.security_type

    def get_security_currency(self):
        self.currency = "USD"
        return self.currency

    def get_security_data(self, client):
        client.get_security_data(self.ticker_symbol)

    def place_order(self,
                    client,
                    action,
                    order_type,
                    order_price=None,
                    quantity=1.0,
                    time_in_force="DAY",
                    transmit=False):
        client.place_order(self.ticker_symbol, action, order_type, order_price,
                           quantity, time_in_force, transmit)
