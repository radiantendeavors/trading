"""!
@package pytrader.libs.dbclient

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


@file __init__.py
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
class EtfInfo(mysql.MySQLDatabase):

    def __init__(self):
        self.table_name = "etf_info"
        super().__init__()

    def select(self, ticker):
        logger.debug("Begin Function")
        sql = """
        SELECT *
        FROM `etf_info`
        WHERE `ticker`=%s
        """
        logger.debug("Ticker: %s", ticker)
        logger.debug("SQL: %s", sql)

        cursor = self.mycursor
        try:
            cursor.execute(sql, (ticker))
            result = cursor.fetchone()
            logger.debug("Result: %s", result)
            return result
        except pymysql.Error as e:
            logger.error("Select Error: %s", e)
            return None

    def select_all_tickers(self):
        logger.debug("Begin Function")
        sql = """
        SELECT `ticker`
        FROM `etf_info`
        """
        logger.debug("SQL: %s", sql)

        cursor = self.mycursor
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            # logger.debug("Result: %s", result)
            return result
        except pymysql.Error as e:
            logger.error("Select Error: %s", e)
            return None

    def insert(self, ticker, name):
        logger.debug("Begin Function")
        sql = """
        INSERT INTO `etf_info`
        (`ticker`, `name`, `first_listed`, `last_seen`)
        VALUES (%s, %s, %s, %s)
        """

        first_listed = date.today()
        last_seen = date.today()

        logger.debug("Ticker: %s", ticker)
        logger.debug("SQL: %s", sql)

        cursor = self.mycursor
        try:
            cursor.execute(sql, (
                ticker,
                name,
                first_listed,
                last_seen,
            ))
        except pymysql.Error as e:
            logger.error("Insert Error: %s", e)

        self.mydb.commit()

        logger.debug("End Function")
        return None

    def update_last_seen(self, ticker, name):
        logger.debug("Begin Function")
        last_seen = date.today()
        cursor = self.mycursor

        sql = """
        UPDATE `etf_info`
        SET `last_seen`=%s, `name`=%s
        WHERE `ticker`=%s
        """

        try:
            cursor.execute(sql, (last_seen, name, ticker))
        except pymysql.Error as e:
            logger.error("Update Error 2: %s", e)

        logger.debug("SQL: %s", sql)
        self.mydb.commit()

        logger.debug("End Function")
        return None

    def update_delisted(self, ticker):
        logger.debug("Begin Function")
        logger.debug("Ticker: %s", ticker)
        delisted = date.today()
        logger.debug("Delisted: %s", delisted)
        cursor = self.mycursor

        ticker_info = self.select(ticker)

        logger.debug("Ticker Info: %s", ticker_info)
        last_seen = ticker_info["last_seen"]
        logger.debug("Last Seen: %s", last_seen)

        days_since_last_seen = delisted - last_seen

        logger.debug("Days Since Last Seen: %s", days_since_last_seen.days)

        if days_since_last_seen.days > 7:
            sql = """
            UPDATE `etf_info`
            SET `delisted_date`=%s
            WHERE `ticker`=%s
            """
            try:
                cursor.execute(sql, (delisted, ticker))
            except pymysql.Error as e:
                logger.error("Update Delisting Error: %s", e)

        logger.debug("SQL: %s", sql)
        self.mydb.commit()

        logger.debug("End Function")
        return None
