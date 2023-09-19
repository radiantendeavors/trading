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
# # System Libraries
# import pymysql
# from datetime import date

# # 3rd Party Libraries

# # Application Libraries
# # System Library Overrides
# from pytrader.libs.system import logging

# # Other Application Libraries
# from pytrader.libs.clients import mysql
# from pytrader.libs.utilities import text

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
# """!
# @var logger
# The base logger.

# @var colortext
# Allows Color text on the console
# """
# logger = logging.getLogger(__name__)
# colortext = text.ConsoleText()

# ==================================================================================================
#
# Classes
#
# ==================================================================================================
# class EtfInfo(mysql.MySQLDatabase):

#     def __init__(self):
#         self.table_name = "etf_info"
#         super().__init__()

#     def select(self, select_clause=None, where_clause=None):
#         logger.debug("Begin Function")

#         if select_clause:
#             sql = """
#             SELECT """ + select_clause + "\n"
#         else:
#             sql = """
#             SELECT *
#             """

#         sql += """FROM `etf_info`
#         """

#         if where_clause:
#             sql += "WHERE " + where_clause

#         logger.debug2("SQL: %s", sql)

#         cursor = self.mycursor
#         try:
#             cursor.execute(sql)
#             result = cursor.fetchall()
#             logger.debug3("Result: %s", result)
#             logger.debug10("End Function")
#             return result
#         except pymysql.Error as e:
#             logger.error("Select Error: %s", e)
#             logger.debug10("End Function")
#             return None

#     def insert(self, ticker, name):
#         logger.debug("Begin Function")
#         sql = """
#         INSERT INTO `etf_info`
#         (`ticker`, `name`, `first_listed`, `last_seen`)
#         VALUES (%s, %s, %s, %s)
#         """

#         first_listed = date.today()
#         last_seen = date.today()

#         logger.debug("Ticker: %s", ticker)
#         logger.debug2("SQL: %s", sql)

#         cursor = self.mycursor
#         try:
#             cursor.execute(sql, (
#                 ticker,
#                 name,
#                 first_listed,
#                 last_seen,
#             ))
#         except pymysql.Error as e:
#             logger.error("Insert Error: %s", e)

#         self.mydb.commit()

#         logger.debug("End Function")
#         return None

#     def update_last_seen(self, ticker, name):
#         logger.debug10("Begin Function")
#         last_seen = date.today()
#         cursor = self.mycursor

#         sql = """
#         UPDATE `etf_info`
#         SET `last_seen`=%s, `name`=%s
#         WHERE `ticker`=%s
#         """

#         try:
#             cursor.execute(sql, (last_seen, name, ticker))
#         except pymysql.Error as e:
#             logger.error("Update Error 2: %s", e)

#         logger.debug("SQL: %s", sql)
#         self.mydb.commit()

#         logger.debug10("End Function")
#         return None

#     def update_delisted(self, ticker):
#         logger.debug10("Begin Function")
#         logger.debug("Ticker: %s", ticker)
#         delisted = date.today()
#         logger.debug("Delisted: %s", delisted)
#         cursor = self.mycursor

#         where = "`ticker`='" + ticker + "'"
#         ticker_info = self.select(where_clause=where)

#         logger.debug("Ticker Info: %s", ticker_info[0])
#         last_seen = ticker_info[0]["last_seen"]
#         logger.debug("Last Seen: %s", last_seen)

#         days_since_last_seen = delisted - last_seen

#         logger.debug("Days Since Last Seen: %s", days_since_last_seen.days)

#         if days_since_last_seen.days > 7 and ticker_info[0][
#                 "delisted_date"] is None:
#             sql = """
#             UPDATE `etf_info`
#             SET `delisted_date`=%s
#             WHERE `ticker`=%s
#             """
#             try:
#                 cursor.execute(sql, (delisted, ticker))
#             except pymysql.Error as e:
#                 logger.error("Update Delisting Error: %s", e)

#             logger.debug("SQL: %s", sql)
#             self.mydb.commit()

#         logger.debug10("End Function")
#         return None

#     def update_ibkr_info(self, symbol, contract_id, primary_exchange,
#                          exchange):
#         logger.debug10("Begin Function")
#         cursor = self.mycursor

#         sql = """
#         UPDATE `etf_info`
#         SET `ibkr_contract_id`=%s, `ibkr_symbol`=%s, `ibkr_primary_exchange`=%s,
#             `ibkr_exchange`=%s
#         WHERE `ticker`=%s
#         """

#         try:
#             cursor.execute(
#                 sql, (contract_id, symbol, primary_exchange, exchange, symbol))
#         except pymysql.Error as e:
#             logger.error("Update Delisting Error: %s", e)

#         logger.debug("SQL: %s", sql)
#         self.mydb.commit()
#         logger.debug10("End Function")
#         return None

#     def update_ibkr_ipo_date(self, symbol, ipo_date):
#         logger.debug10("Begin Function")
#         cursor = self.mycursor

#         sql = """
#         UPDATE `etf_info`
#         SET `ipo_date`=%s
#         WHERE `ticker`=%s
#         """

#         try:
#             cursor.execute(sql, (ipo_date, symbol))
#         except pymysql.Error as e:
#             logger.error("Update Delisting Error: %s", e)

#         logger.debug("SQL: %s", sql)
#         self.mydb.commit()
#         logger.debug10("End Function")
#         return None

#     def update_yahoo_info(self, ticker, yahoo_security=None):
#         logger.debug10("Begin Function")

#         cursor = self.mycursor
#         if yahoo_security is None:
#             yahoo_security = ticker

#         sql = """
#         UPDATE `etf_info`
#         SET `yahoo_symbol`=%s
#         WHERE `ticker`=%s
#         """

#         logger.debug("Ticker: %s", ticker)
#         logger.debug("Yahoo Security: %s", yahoo_security)

#         try:
#             cursor.execute(sql, (yahoo_security, ticker))
#         except pymysql.Error as e:
#             logger.error("Update Interactive Brokers Information Error: %s", e)

#         logger.debug("SQL: %s", sql)
#         self.mydb.commit()
#         logger.debug10("End Function")
#         return None
