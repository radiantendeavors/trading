/**************************************************************************************************
 *                                                                                                *
 * Trader                                                                                         *
 *                                                                                                *
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
// C sytem headers


// C++ standard library headers
#include <iostream>

// TWS API Specific Headers
#include <twsapi/StdAfx.h>

// Local Headers
#include "include/client.hpp"

/**************************************************************************************************
 *                                                                                                *
 * Main                                                                                           *
 *                                                                                                *
 **************************************************************************************************/
int main(int argc, char** argv) {

  unsigned int attempt = 0;
  const unsigned int max_attempts = 50;

  std::cout << "Start C++ Socket Client Test" << std::endl;

  while (attempt <= max_attempts) {
    ++attempt;
    std::cout << "Attempt " << attempt << " of " << max_attempts << "." << std::endl;


  }
  return 0;
}
