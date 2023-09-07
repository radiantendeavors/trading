"""!@package pytrader.libs.utilities.exceptions

Testing Strategy

@author G. S. Derber
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

@file pytrader/libs/utilities/exceptions.py

Testing Strategy

"""


class TraderException(Exception):
    """!
    Trader Exception
    """


class BrokerError(Exception):
    """!
    Used for Broker related errors
    """


class BrokerNotConnectedError(BrokerError):
    """!
    Used for Broker Not Connected Errors
    """


class BrokerNotAvailable(BrokerError):
    """!
    Used if the Broker Port is not available.
    """


class BrokerWarning(Warning):
    """!
    Used for Broker Related Warnings
    """


class BrokerTooManyRequests(BrokerWarning):
    """!
    Used when there are too many outstanding data requests.
    """


class InvalidExchange(BrokerWarning):
    """!
    Used when an invalid exchange is requeusted.
    """


class InvalidTickType(BrokerWarning):
    """!
    Used for invalid tick types.
    """


class RuntimeWarning(Warning):
    """!
    Used to track run time warnings.
    """


class NotImplementedWarning(RuntimeWarning):
    """!
    Used to raise a warning when a feature is not implemented and can be safely ignored.
    """
