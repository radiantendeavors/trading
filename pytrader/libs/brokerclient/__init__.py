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
from pytrader.libs.brokerclient import ibkrclient
from pytrader.libs.utilities import config

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
class BrokerClient(ibkrclient.IbkrClient):

    def __init__(self, address, port, client_id=0):
        self.req_id = 0
        self.address = address
        self.port = port
        self.client_id = client_id
        super(BrokerClient, self).__init__(address, port, client_id)

    def check_server(self):
        self.reqCurrentTime()
        if self.serverVersion() is not None:
            logger.info("Server Version: %s", self.serverVersion())
        else:
            logger.error(
                "Failed to connect to the server: Server Version Unknown")
        if self.twsConnectionTime() is not None:
            logger.info("Connection time: %s",
                        self.twsConnectionTime().decode())
        else:
            logger.error(
                "Failed to connect to the server: Connection Time Unknown")

    def set_contract(self,
                     security,
                     security_type="STK",
                     exchange="SMART",
                     currency="USD"):
        contract = Contract()
        contract.symbol = security
        contract.secType = security_type
        contract.exchange = exchange
        contract.currency = currency

        self.contract = contract

    def get_security_data(self):
        self.req_id += 1

        self.reqContractDetails(self.req_id, self.contract)
        time.sleep(10)

    def get_security_pricing_data(self):
        self.req_id += 1
        self.reqMktData(self.req_id, self.contract, "233", False, False, [])

    def get_option_chain(self):
        self.req_id += 1
        security = self.contract.symbol
        security_type = self.contract.secType
        logger.debug("Contract ID: %s", self.contract.contract_id)
        contract_id = self.contract.contract_id

        logger.debug10("Get the Option Chain")
        logger.debug2("Request ID: %s", self.req_id)
        logger.debug("Security:%s", security)
        logger.debug("Security Type: %s", security_type)
        logger.debug("Contract ID: %s", contract_id)
        self.reqSecDefOptParams(self.req_id, security, "", security_type,
                                contract_id)
        time.sleep(60)

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

        if self.nextValidOrderId:
            logger.info("Order IDs: %s", self.nextValidOrderId)
            self.placeOrder(self.nextValidOrderId, contract, order)
            time.sleep(5)

            logger.debug("Requesting Open Orders")
            self.reqOpenOrders()
            time.sleep(20)
            logger.debug("Requesting All Open Orders")
            self.reqAllOpenOrders()
            time.sleep(30)
        else:
            logger.error("Order ID not received.  Ending application.")
            sys.exit()

    def get_open_positions(self):
        self.reqPositions()

    def get_account_summary(self):
        self.req_id += 1
        self.reqAccountSummary(self.req_id, "ALL",
                               "AccountType, AvailableFunds")

    def get_security_details(self, security):
        self.req_id += 1

        contract = Contract()
        contract.symbol = security
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"

        self.reqContractDetails(self.req_id, security)
