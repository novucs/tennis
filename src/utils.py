#!/usr/bin/env python

"""

General utilities used by both tennis player ranking solutions.

"""

import os

import numpy as np

from linked_list import List

# Define the two possible genders.
MALE = False
FEMALE = True

# Define pretty banners.
HEADER = "\n" + "-" * 40 + "\n\n"
FOOTER = "\n\n" + "-" * 40 + "\n"


def parse_csv_line(line):
    """Parses a CSV (comma separated values) line.

    :param line: The line to parse.
    :return: The array of values in this line.
    """

    if line == "":
        return np.empty(0)

    values = List()
    value = ""
    quotes = False

    for character in line:
        if character == '\n':
            break
        elif character == '"':
            quotes = not quotes
        elif not quotes and character == ',':
            values.append(value)
            value = ""
        else:
            value += character

    values.append(value)
    return values.to_array()


def prepare_persist(file_name):
    # Delete file if already exists.
    if os.path.isfile(file_name):
        os.remove(file_name)

    # Ensure directory exists.
    directory_name = os.path.dirname(os.path.realpath(file_name))
    if not os.path.isdir(directory_name):
        os.makedirs(directory_name)
