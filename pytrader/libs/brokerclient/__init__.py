# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import logging
import sys
import time

# 3rd Party libraries
from ibapi.client import Contract
from ibapi.order import Order

# System Library Overrides

# Application Libraries
from pytrader import DEBUG
from pytrader.libs.brokerclient import ibkrclient

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
# ==================================================================================================
#
# Class brokerclient
#
# ==================================================================================================
class BrokerClient():

    def __init__(self, address, port, client_id=0):
        self.address = address
        self.port = port
        self.client_id = client_id

    def connect(self):
        self.client = ibkrclient.IbkrClient(self.address, self.port,
                                            self.client_id)

    def check_server_time(self):
        self.client.reqCurrentTime()

    def place_order(self,
                    security,
                    action,
                    order_type,
                    order_price=None,
                    quantity=1.0):

        # Request details for the stock
        contract = Contract()
        contract.symbol = security
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        # Define limit order
        order = Order()
        order.action = action
        order.totalQuanitity = quantity
        order.orderType = order_type

        if order_type == "LMT":
            order.lmtPrice = order_price

        order.transmit = False

        if self.client.orderId:
            print("Order IDs: ", self.client.orderId)
            self.client.placeOrder(self.client.orderId, contract, order)
            time.sleep(5)
        else:
            print("Order ID not received.  Ending application.")
            sys.exit()

        client.reqAccountSummary(0, "ALL", "AccountType, AvailableFunds")
        client.reqPositions()

    def get_security_details(self, security):
        self.client.reqContractDetails(0, security)

    def disconnect(self):
        self.client.disconnect()
