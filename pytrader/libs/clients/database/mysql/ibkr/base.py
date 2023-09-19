"""!
@package pytrader.libs.clients.database.mysql.ibkr.base.py

Provides the base class for Interactive Brokers Database Tables

@author G S Derber
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


@file pytrader/libs/clients/database/mysql/ibkr/base.py
"""
# System Libraries
from datetime import date
from typing import Optional

# 3rd Party Libraries
import pymysql

# Application Libraries
from pytrader.libs.clients.database import mysql
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrBase(mysql.MySQLDatabase):
    """!
    Base Class for all Interactive Brokers Database Tables.
    """

    table_name = None
    insert_column_names = None
    update_column_names = None

    def select(self, select_columns: Optional[list] = None, criteria: Optional[dict] = None):
        """!
        Query table
        """
        sql_input = []

        if select_columns:
            select_string = self.substitute_list(select_columns)
            sql_input += select_columns
        else:
            select_string = "*"

        sql = (f"SELECT {select_string}\n"
               f"FROM {self.table_name}")

        if criteria:
            x = 0
            for col_name, values in criteria.items():
                value_string = self.substitute_list(values)
                if x == 0:
                    sql += f"\nWHERE `{col_name}` IN ({value_string})"
                else:
                    # TODO: Determine how to add additional criteria.
                    sql += ""
                sql_input += values
        self._execute(sql, sql_input)
        return self.mycursor.fetchall()

    def insert(self, columns: list) -> None:
        """!
        Inserts a new row into the table.

        @param columns: The data to insert.

        @return None.
        """
        criteria_column_name = self.insert_column_names[0]
        criteria = {criteria_column_name: [columns[0]]}
        row_exists = self.select([criteria_column_name], criteria)

        if row_exists:
            self._update(columns)
        else:
            self._insert(columns)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _execute(self, sql: str, values: Optional[list] = None) -> None:
        query_type = sql.split(" ")[0]
        logger.debug("\nSQL\n%s Values: %s", sql, values)
        try:
            if values:
                self.mycursor.execute(sql, values)
            else:
                self.mycursor.execute(sql)
        except pymysql.Error as msg:
            logger.error("%s Error: %s", query_type, msg)

    def _insert(self, columns: list) -> None:
        column_string = self.substitute_list(columns)
        column_names = ", ".join(self.insert_column_names)
        sql = (f"INSERT INTO `{self.table_name}`\n"
               f"({column_names})\n"
               f"VALUES ({column_string})")
        self._execute(sql, columns)
        self.mydb.commit()

    def _update(self, columns: list) -> None:
        column_names = "`=%s, `".join(self.update_column_names) + "`=%s"
        column_names = "`" + column_names
        sql = (f"UPDATE `{self.table_name}`\n"
               f"SET {column_names}\n"
               f"WHERE `{self.update_column_names[0]}`={columns[0]}")
        columns.append(date.today())
        self._execute(sql, columns)
        self.mydb.commit()