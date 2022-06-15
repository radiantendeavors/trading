/**************************************************************************************************
 *                                                                                                *
 * brokerclient.cpp                                                                               *
 *                                                                                                *
 * This file is part of trader.                                                                   *
 * Copyright (C) by G Derber <gd.github@radiantendeavors.com>                                     *
 *                                                                                                *
 * This program is free software; you can redistribute and/or modify it under the terms of the    *
 * GNU Affero General Public License v3.0 as published by the Free Software Foundation            *
 *                                                                                                *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;      *
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See  *
 * the GNU Affero General Public License for more details.                                        *
 *                                                                                                *
 **************************************************************************************************/
#define _CRT_SECURE_NO_WARNINGS

#include "brokerclient.hpp"

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

// Receive and display the current time
void BrokerClient::currentTime(long curTime) {
  time_t epoch = curTime;
  std::cout << "Current time: " << asctime(localtime(&epoch)) << std::endl;
}

// Respond to errors
void BrokerClient::error(int id, int code, const std::string& msg,
                         const std::string& advancedOrderRejectJson) {
  std::cout << "Error: " << code << ": " << msg << std::endl;
}

