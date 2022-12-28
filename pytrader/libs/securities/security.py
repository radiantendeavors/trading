"""!
@package pytrader.libs.security

Provides the broker client

@author Geoff S. derber
@version HEAD
@date 2022
@copyright GNU Affero General Public License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


@file security.py
"""
# System libraries
import sys
import time

# 3rd Party libraries
from ibapi.client import Contract
from ibapi.order import Order

# System Library Overrides
from pytrader.libs.system import logging

# Application Libraries
from pytrader.libs.clients import broker

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
