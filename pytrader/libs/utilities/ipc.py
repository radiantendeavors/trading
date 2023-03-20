"""!@package pytrader.libs.utilities.ipc

The main user interface for the trading program.

@author G. S. Derber
@version HEAD
@date 2022-2023
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

@file pytrader/libs/utilities/ipc.py
"""
# System Libraries
import json
import socket
import os
import threading

from abc import ABCMeta, abstractmethod

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

"""
logger = logging.getLogger(__name__)

HOME = os.path.expanduser("~") + "/"
CONFIG_DIR = HOME + ".config/investing"
SOCKET_FILE = CONFIG_DIR + "/socket"

HEADER = 32
DISCONNECT_MESSAGE = "!DISCONNECT"
FORMAT = "utf-8"


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class Ipc():

    __metaclass__ = ABCMeta

    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def start_thread(self, queue):
        self.queue = queue

        while True:
            connection, client_address = self.sock.accept()
            thread = threading.Thread(target=self.run,
                                      args=(connection, client_address),
                                      daemon=True)
            thread.start()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    def send(self, msg, connection=None):
        if connection is None:
            connection = self.sock

        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        logger.debug("Message Length: %s", send_length)
        logger.debug("Message: %s", message)
        connection.sendall(send_length)
        connection.sendall(message)

    @abstractmethod
    def recv(self, connection=None):
        if connection is None:
            connection = self.sock

        logger.debug("Begin Function")
        header_msg = connection.recv(HEADER).decode(FORMAT)
        logger.debug("Header Message: %s", header_msg)

        if header_msg:
            msg_length = int(header_msg)
            data = connection.recv(msg_length)
            data_str = data.decode(FORMAT)
            logger.debug("Data String: %s", data_str)

        logger.debug("End Function")

        return data_str


class IpcServer(Ipc):

    def __init__(self):
        super().__init__()
        self.queue = None

        try:
            os.unlink(SOCKET_FILE)
        except OSError:
            if os.path.exists(SOCKET_FILE):
                raise FileExistsError

        logger.debug("Bind to socket: %s", SOCKET_FILE)
        self.sock.bind(SOCKET_FILE)
        self.sock.listen(5)

    def run(self, connection, client_address):
        logger.debug("Waiting for a connection")

        #try:
        logger.debug("Client Address: %s", client_address)

        client_connected = True
        while client_connected:
            data_str = self.recv(connection)
            logger.debug("Received: %s", data_str)

            if data_str == DISCONNECT_MESSAGE:
                logger.debug("Client Disconnected")
                client_connected = False
            else:
                logger.debug("Sending Data back to the client")
                #data_obj = json.loads(data)

                # if data_obj.get("tickers"):
                #     self._create_contracts(data_obj["tickers"])

                self.send(data_str, connection)

        #finally:
        logger.debug("Closing Socket")
        connection.close()


class IpcClient(Ipc):

    def __init__(self):
        super().__init__()

    def connect(self):
        try:
            self.sock.connect(SOCKET_FILE)
        except socket.error as msg:
            logger.debug("Error Connecting: %s", msg)

    def disconnect(self):
        self.send(DISCONNECT_MESSAGE)
        logger.debug("Closing Socket")
        self.sock.close()


class Message():

    def __init__(self, message):
        self.message = message

    def to_json(self):
        self.message_json = json.dumps(self.message)
        return self.message_json
