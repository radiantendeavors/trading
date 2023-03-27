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
    """!
    Base Class for Interprocess Communication
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connection = None

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    def send(self, msg):
        connection = self._get_connection()

        message = Message(msg)
        message.encode()
        msg_length = message.get_length()
        header_message = HeaderMessage(msg_length)
        header_message.encode()
        header_message.set_header()

        header_message.send(connection)
        message.send(connection)

    def recv(self):
        logger.debug10("Begin Function")
        connection = self._get_connection()
        message_str = None

        header_msg = connection.recv(HEADER)
        logger.debug4("Header Message: %s", header_msg)
        header_msg = header_msg.decode(FORMAT)
        logger.debug4("Header Message: %s", header_msg)

        if len(header_msg) == HEADER:
            msg_length = int(header_msg)
            msg = connection.recv(msg_length)
            logger.debug3("Message: %s", msg)
            message_str = msg.decode(FORMAT)
            logger.debug3("Message String: %s", message_str)

        else:
            logger.error("Invalid Header")
            logger.error("Header Msg: %s", header_msg)

        logger.debug10("End Function")

        return message_str

    def _get_connection(self):
        if self.connection is None:
            connection = self.sock
        else:
            connection = self.connection

        return connection


class IpcServer(Ipc):

    def __init__(self):
        super().__init__()
        self.recv_queue = None
        self.send_queue = None
        self.client_connected = False

        try:
            os.unlink(SOCKET_FILE)
        except OSError:
            if os.path.exists(SOCKET_FILE):
                raise FileExistsError

        logger.debug("Bind to socket: %s", SOCKET_FILE)
        self.sock.bind(SOCKET_FILE)
        self.sock.listen(5)

    def send_loop(self):
        while self.client_connected:
            message = self.send_queue.get()
            self.send(message)

    def recv_loop(self, client_address):
        logger.debug("Waiting for a connection")

        try:
            logger.debug("Client Address: %s", client_address)

            self.client_connected = True
            send_thread = threading.Thread(target=self.send_loop, daemon=True)
            send_thread.start()

            while self.client_connected:
                data_str = self.recv()
                logger.debug("Received: %s", data_str)

                if data_str == DISCONNECT_MESSAGE:
                    logger.debug("Client Disconnected")
                    self.client_connected = False
                else:
                    logger.debug("Sending Data to Broker")

                    data_obj = json.loads(data_str)

                    if data_obj:
                        logger.debug("Data Obj: %s", data_obj)
                        self.recv_queue.put(data_obj)

        finally:
            logger.debug("Closing Socket")
            self.connection.close()

    def start_thread(self, recv_queue, send_queue):
        self.recv_queue = recv_queue
        self.send_queue = send_queue

        self.connection, client_address = self.sock.accept()
        recv_thread = threading.Thread(target=self.recv_loop,
                                       args=(client_address, ),
                                       daemon=True)
        recv_thread.start()


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
        ## The message
        self.message = message

        ## Encoded Message
        self.encoded_message = None

        ## The encoding format
        self.format = "utf-8"

    def to_json(self):
        self.message = json.dumps(self.message)
        return self.message

    def to_dict(self):
        message = json.load(self.message)
        return message

    def encode(self):
        # Ensure we have a string to encode
        self._to_str()

        self.encoded_message = self.message.encode(self.format)
        return self.encoded_message

    def get_length(self):
        if self.encoded_message is None:
            self.encode()

        self.msg_length = len(self.encoded_message)
        return self.msg_length

    def send(self, connection):
        logger.debug2("Message to send: %s", self.message)
        logger.debug3("Sending Encoded Message: %s", self.encoded_message)
        connection.sendall(self.encoded_message)

    def _to_str(self):
        if isinstance(self.message, dict):
            self.to_json()

        if isinstance(self.message, int):
            self.message = str(self.message)


class HeaderMessage(Message):

    def __init__(self, message):
        self.header = HEADER
        super().__init__(message)

    def set_header(self):
        self.encoded_message += b' ' * (HEADER - len(self.encoded_message))
