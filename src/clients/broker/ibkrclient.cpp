/**************************************************************************************************
 *
 * @file brokerclient/brokerclient.cpp
 *
 * This file is part of trader.
 * @author G Derber
 * @version HEAD
 * @date 2022
 * Copyright (C) by G Derber <gd.github@radiantendeavors.com>
 *
 * This program is free software; you can redistribute and/or modify it under the terms of the
 * GNU Affero General Public License v3.0 as published by the Free Software Foundation
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
 * the GNU Affero General Public License for more details.
 *
 **************************************************************************************************/
#define _CRT_SECURE_NO_WARNINGS

#include "brokerclient.hpp"

/***************************************************************************************************
 *
 * Class Brokerclient
 *
 * @param host Provides the hostname or IP address to connect to.
 * @param port Provides the port to connect to.
 * @param clientId Provides the Client Id for the connection.
 *
 **************************************************************************************************/
BrokerClient::BrokerClient(const char* host, int port, int clientId) :
  signal(1000), EClientSocket(this, &signal) {

  // Connect to TWS / IB Gateway
  bool conn = eConnect(host, port, clientId, false);

  if (conn) {

    // Launch reader thread
    reader = new EReader(this, &signal);
    reader -> start();
  } else {
    std::cout << "Failed to connect" << std::endl;
  }
}

BrokerClient::~BrokerClient() { delete reader; }
