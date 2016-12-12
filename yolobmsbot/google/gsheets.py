# !/usr/bin/python
# coding: utf_8

# Copyright 2016-2017 RaceUP ED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time

from .. import utils
from yolobmsbot.google import gauthenticator


# spreadsheet ids
SPREADSHEET_SEGMENT_ID = [
    "1JO_TVT6BmutOljqCMCosNuywod1UptAuRrWhADV5Cgg",
    "1WibWQiZXTVH7ivu7tSlpO6nBvxPVUIKc4aVt8z7sips",
    "1Md0W21F-xhB8hDQJcfPYHI-R4MFcqZdttsstEhApkXQ",
    "1mGynNdQcvm6AH8WSeFb10ukfgwMe9x1YOt1zjGpnkOw",
    "12vr6tSJ-RBlN2SPLpHI7fMJ9lJoDN9IBg3ORO6c_MlM",
    "1lulGvUka5pvh5-apoFMGeyAuQr5sNdmqy1DCfBhRJhI",
    "14KQ4mJGsHrh22H-oy5IMRLi9lb3l9PyWvyaTtDkGitU",
    "16S-6XdZJnl7JFUN03XmtwunR_hl7cQLXUihYT8ATIek"
]  # IDs of google sheets for each segment
SPREADSHEET_PACK_ID = "1h80UuDc68Fc0ZlBTcIXRSdF-Zl06q3dj2y8SvSl6Mok"  # IDs of google sheets for entire pack

# spreadsheet cells
SPREADSHEET_SEGMENT_MAX_COLUMN = "S"  # max column in a typical segment spreadsheet
SPREADSHEET_PACK_MAX_COLUMN = "I"  # max column in a typical pack spreadsheet
SPREADSHEETS_MIN_COLUMN = "A"  # min column in spreadsheets
SPREADSHEETS_MIN_ROW = "2"  # mIN row in spreadsheets
SPREADSHEETS_MAX_ROW = "5001"  # max row in spreadsheets
SPREADSHEETS_TOP_LEFT_CORNER = SPREADSHEETS_MIN_COLUMN + SPREADSHEETS_MIN_ROW  # top left corner in spreadsheets0
SPREADSHEET_COLUMNS = ["B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S"]


def get_last_row_of_column(spreadsheet, column, max_rows=9999):
    """
    :param spreadsheet: string
        Spreadsheet ID
    :param column: string
        Column to get last row of
    :param max_rows: int
        Max rows to search
    :return: int
        Number of last row
    """

    service = gauthenticator.create_gdrive_driver()
    for row in range(1, max_rows):
        range_name = column + str(row)
        try:
            value = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet, range=range_name
            ).execute().get("values", [])[0]  # get values
            if len(str(value)) < 1:  # if cell is empty
                return row - 1
        except:
            return row - 1
    return max_rows


def get_last_segment_value(segment):
    """
    :param segment: int
        Number of segment of cell (starts from 0)
    :return: double, string
        Last value of cell, time of last update
    """

    service = gauthenticator.create_gdrive_driver()  # get new sheets instance
    column = SPREADSHEET_COLUMNS[segment]  # get column of segment
    row = get_last_row_of_column(SPREADSHEET_PACK_ID, column)  # get row of last cell

    data_value = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_PACK_ID, range=column + str(row)
    ).execute().get("values", [])[0][0]  # get cell value
    data_time = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_PACK_ID, range=SPREADSHEETS_MIN_COLUMN + str(row)
    ).execute().get("values", [])[0][0]  # get time value

    return data_value, data_time


def get_last_cell_value(cell, segment):
    """
    :param cell: int
        Number of cell (starts from 0)
    :param segment: int
        Number of segment of cell (starts from 0)
    :return: double, string
        Last value of cell, time of last update
    """

    service = gauthenticator.create_gdrive_driver()  # get new sheets instance
    column = SPREADSHEET_COLUMNS[cell]  # get column of segment
    row = get_last_row_of_column(SPREADSHEET_SEGMENT_ID[segment], column)  # get row of last cell

    data_value = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_SEGMENT_ID[segment], range=column + str(row)
    ).execute().get("values", [])[0][0]  # get cell value
    data_time = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_SEGMENT_ID[segment], range=SPREADSHEETS_MIN_COLUMN + str(row)
    ).execute().get("values", [])[0][0]  # get time value

    return data_value, data_time
