#!/usr/bin/env python3
#-----------------------------------------------------------------------
#
#
# Text
#
#   ....
#
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
#
# Libraries
#
#-----------------------------------------------------------------------

# System Libraries
import sys
import os
import math

# 3rd Party Libraries

# Application Libraries
# Application System Overrides
from pytrader.libs.system import logging

#-----------------------------------------------------------------------
#
# Global Variables
#
#-----------------------------------------------------------------------
# Enable Logging
# create logger
logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------
#
# Classes
#
# ConsoleText
#
#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
#
# Class ConsoleText
#
# ...
#
# Inputs
# ------
#    ...
#
# Returns
# -------
#    None
#
# Raises
# ------
#    ...
#
#-----------------------------------------------------------------------
class ConsoleText():

    def __init__(self):
        self.escape = "\x1b["

        self.attributes = {
            "none": 0,
            "bold": 1,
            "unk_a": 2,
            "unk_b": 3,
            "underline": 4,
            "blink": 5,
            "unk_c": 6,
            "reverse": 7
        }

        self.fgcolors = {
            "black": 30,
            "red": 31,
            "green": 32,
            "yellow": 33,
            "blue": 34,
            "fuchsia": 35,
            "magenta": 35,
            "turquoise": 36,
            "cyan": 36,
            "white": 37
        }

        self.bgcolors = {
            "black": 40,
            "red": 41,
            "green": 42,
            "yellow": 43,
            "blue": 44,
            "fuchsia": 45,
            "magenta": 45,
            "turquoise": 46,
            "cyan": 46,
            "white": 47
        }

        return

    #-------------------------------------------------------------------------------
    #
    # Function colorize
    #
    # ...
    #
    # Inputs
    # ------
    #    @param:
    #
    # Returns
    # -------
    #    textstring -
    #
    # Raises
    # ------
    #    ...
    #
    #
    #-------------------------------------------------------------------------------
    def colorize(self,
                 text,
                 attribute="none",
                 fgcolor="white",
                 bgcolor="black"):
        if attribute in self.attributes:
            begincolor = self.escape + str(self.attributes[attribute])
        else:
            begincolor = self.escape + str(self.attributes['none'])

        if fgcolor in self.fgcolors:
            begincolor = begincolor + ";" + str(self.fgcolors[fgcolor])
        else:
            begincolor = begincolor + ";" + str(self.fgcolors['white'])

        if bgcolor in self.bgcolors:
            begincolor = begincolor + ";" + str(self.bgcolors[bgcolor]) + "m"
        else:
            begincolor = begincolor + ";" + str(self.bgcolors['black']) + "m"

        resetcolor = self.escape + str(self.attributes['none']) + ";" + str(
            self.fgcolors['white']) + ";" + str(self.bgcolors['black']) + "m"

        textstring = begincolor + text + resetcolor
        return textstring


#-------------------------------------------------------------------------------
#
# Function column_print
#
# Prints input list in columns
# ...
#
# Inputs
# ------
#    @param: list_to_print = List to Print
#    @param: cols          = The number of columns to use
#    @param: columnwise    = To print by row or column
#    @param: gap           = The gap between columns
#
# Returns
# -------
#    none
#
# Raises
# ------
#    ...
#
#-------------------------------------------------------------------------------
def column_print(obj, cols=4, columnwise=True, gap=4):
    """
    Print the given list in evenly-spaced columns.

    Parameters
    ----------
    obj : list
        The list to be printed.
    cols : int
        The number of columns in which the list should be printed.
    columnwise : bool, default=True
        If True, the items in the list will be printed column-wise.
        If False the items in the list will be printed row-wise.
    gap : int
        The number of spaces that should separate the longest column
        item/s from the next column. This is the effective spacing
        between columns based on the maximum len() of the list items.
    """

    term_height, term_width = os.popen('stty size', 'r').read().split()

    column_width = int(term_width)

    sobj = [str(item) for item in obj]
    if cols > len(sobj):
        cols = len(sobj)

    imax = max([len(item) for item in sobj])
    cmax = column_width // cols

    max_len = min(imax, cmax - gap)

    if columnwise:
        cols = int(math.ceil(float(len(sobj)) / float(cols)))

    plist = [sobj[i:i + cols] for i in range(0, len(sobj), cols)]
    if columnwise:
        if not len(plist[-1]) == cols:
            plist[-1].extend([''] * (len(sobj) - len(plist[-1])))
        plist = zip(*plist)
    printer = '\n'.join([
        ''.join([c[0:max_len].ljust(max_len + gap) for c in p]) for p in plist
    ])
    logger.info1(printer)


#    term_height, term_width = os.popen('stty size', 'r').read().split()
#    total_columns = int(term_width) // column_width
#    total_rows = len(list_to_print) // total_columns
#    # ceil
#    total_rows = total_rows + 1 if len(list_to_print) % total_columns != 0 else total_rows

#   format_string = "".join(["{%d:<%ds}" % (c, column_width) \
#            for c in range(total_columns)])
#    for row in range(total_rows):
#        column_items = []
#        for column in range(total_columns):
#            # top-down order
#           list_index = row + column*total_rows
#            # left-right order
#            #list_index = row*total_columns + column
#            if list_index < len(list_to_print):
#                column_items.append(list_to_print[list_index])
#            else:
#                column_items.append("")
#       print(format_string.format(*column_items))
