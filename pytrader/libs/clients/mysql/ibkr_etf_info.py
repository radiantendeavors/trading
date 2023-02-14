"""!
@package pytrader.libs.clients.mysql.etf_info

Provides the database client

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


@file pytrader/libs/clients/mysql/etf_info.py
"""
# System Libraries
import pymysql
from datetime import date

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients import mysql
from pytrader.libs.utilities import text

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)
colortext = text.ConsoleText()


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrEtfContracts(mysql.MySQLDatabase):

    def __init__(self):
        self.table_name = "z_ibkr_etf_contracts"
        super().__init__()

    def select(self, select_clause=None, where_clause=None):
        logger.debug("Begin Function")

        if select_clause:
            sql = """
            SELECT """ + select_clause + "\n"
        else:
            sql = """
            SELECT *
            """

        sql += """FROM `z_ibkr_etf_contracts`
        """

        if where_clause:
            sql += "WHERE " + where_clause

        logger.debug2("SQL: %s", sql)

        cursor = self.mycursor
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            logger.debug3("Result: %s", result)
            logger.debug10("End Function")
            return result
        except pymysql.Error as e:
            logger.error("Select Error: %s", e)
            logger.debug10("End Function")
            return None

    def insert(self, contract_id, ticker_symbol, security_type, exchange,
               currency, local_symbol, primary_exchange, trading_class):
        logger.debug10("Begin Function")
        logger.debug("Contract ID: %s", contract_id)
        logger.debug("Ticker: %s", ticker_symbol)

        logger.debug("Primary Exchange: %s", primary_exchange)
        logger.debug("Exchange: %s", exchange)
        sql = """
        INSERT INTO `z_ibkr_etf_contracts`
        (`contract_id`, `ticker_symbol`, `security_type`, `exchange`, `currency`, `local_symbol`, `primary_exchange`, `trading_class`)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        logger.debug2("SQL: %s", sql)

        cursor = self.mycursor
        try:
            cursor.execute(sql,
                           (contract_id, ticker_symbol, exchange, currency,
                            local_symbol, primary_exchange, trading_class))
        except pymysql.Error as e:
            logger.error("Insert Error: %s", e)

        self.mydb.commit()

        logger.debug("End Function")
        return None
