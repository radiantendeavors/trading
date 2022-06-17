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
        self.req_id = 0
        self.address = address
        self.port = port
        self.client_id = client_id

    def connect(self):
        self.client = ibkrclient.IbkrClient(self.address, self.port,
                                            self.client_id)

    def check_server_time(self):
        self.client.reqCurrentTime()

    def get_security_data(self, security):
        self.req_id += 1

        contract = Contract()
        contract.symbol = security
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        self.client.reqMktData(self.req_id, contract, "233", False, False, [])
        time.sleep(10)

    def place_order(self,
                    security,
                    action,
                    order_type,
                    order_price=None,
                    quantity=1.0):

        self.req_id += 1

        print(security)
        print(action)
        print(order_type)
        print(order_price)
        print(quantity)

        # Request details for the stock
        contract = Contract()
        contract.symbol = security
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        # Define limit order
        order = Order()
        order.action = action
        order.totalQuantity = quantity
        order.orderType = order_type
        order.tif = "DAY"

        if order_type == "LMT":
            order.lmtPrice = order_price

        order.transmit = False

        time.sleep(10)

        print(contract)
        print(order)
        if self.client.nextValidOrderId:
            print("Order IDs: ", self.client.nextValidOrderId)
            self.client.placeOrder(self.client.nextValidOrderId, contract,
                                   order)
            time.sleep(5)
        else:
            print("Order ID not received.  Ending application.")
            sys.exit()

        self.client.reqAccountSummary(self.req_id, "ALL",
                                      "AccountType, AvailableFunds")
        self.client.reqPositions()

    def get_security_details(self, security):
        self.req_id += 1

        contract = Contract()
        contract.symbol = security
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        self.client.reqContractDetails(self.req_id, security)

    def disconnect(self):
        self.client.disconnect()
