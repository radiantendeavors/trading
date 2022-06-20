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
        try:
            self.client = ibkrclient.IbkrClient(self.address, self.port,
                                                self.client_id)
            return 0
        except Exception as msg:
            logger.error(msg)
            return 1

    def check_server(self):
        self.client.reqCurrentTime()
        logger.info("Server Version: %s", self.client.serverVersion())
        logger.info("Connection time: %s",
                    self.client.twsConnectionTime().decode())

    def get_security_data(self,
                          security,
                          security_type="STK",
                          exchange="SMART",
                          currency="USD"):
        self.req_id += 1

        contract = Contract()
        contract.symbol = security
        contract.secType = security_type
        contract.exchange = exchange
        contract.currency = currency
        self.client.reqMktData(self.req_id, contract, "233", False, False, [])
        time.sleep(10)

    def place_order(self,
                    security,
                    action,
                    order_type,
                    order_price=None,
                    quantity=1.0,
                    time_in_force="DAY",
                    transmit=False):
        self.req_id += 1

        logger.debug("BrokerClient.place_order")
        logger.debug("Security: %s", security)
        logger.debug("Action: %s", action)
        logger.debug("Order Type: %s", order_type)
        logger.debug("Order Price: %s", order_price)
        logger.debug("Quantity: %s", quantity)
        logger.debug("Time in Force: %s", time_in_force)
        logger.debug("Transmit: %s", transmit)

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
        order.tif = time_in_force

        if order_type == "LMT":
            order.lmtPrice = order_price

        order.transmit = transmit

        time.sleep(10)

        logger.debug("Contract: %s", contract)
        logger.debug("Order: %s", order)

        if self.client.nextValidOrderId:
            logger.info("Order IDs: %s", self.client.nextValidOrderId)
            self.client.placeOrder(self.client.nextValidOrderId, contract,
                                   order)
            time.sleep(5)

            logger.debug("Requesting Open Orders")
            self.client.reqOpenOrders()
            time.sleep(20)
            logger.debug("Requesting All Open Orders")
            self.client.reqAllOpenOrders()
            time.sleep(30)
        else:
            logger.error("Order ID not received.  Ending application.")
            sys.exit()

    def get_open_positions(self):
        self.client.reqPositions()

    def get_account_summary(self):
        self.req_id += 1
        self.client.reqAccountSummary(self.req_id, "ALL",
                                      "AccountType, AvailableFunds")

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
