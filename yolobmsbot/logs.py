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

import os
import time
from datetime import datetime

DATETIME_NOW = datetime.now()
SCRIPT_DIRECTORY = os.path.dirname(__file__)  # path to directory of python script running
LOG_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), str(int(time.time())) + "-logs")
if not os.path.exists(LOG_FOLDER):  # create necessary folders
    os.makedirs(LOG_FOLDER)
LOG_FILES = [os.path.join(LOG_FOLDER, "users.csv"), os.path.join(LOG_FOLDER, "actions.csv")]


def log_users(user_id, user_first_name, user_last_name, user_username):
    """
    :param user_id: str
        User id to log
    :param user_first_name: str
        User first name to log
    :param user_last_name: str
        User last name to log
    :param user_username: str
        User name to log
    :return: void
        Log user name to log file
    """

    log_values_to_file(
        LOG_FILES[0],
        [
            str(datetime.now()), str(user_id), str(user_first_name), str(user_last_name), str(user_username)
        ]
    )


def log_user_action(user, action):
    """
    :param user: str
        User name to log
    :param action: str
        What user did
    :return: void
        Log user name and action to log file
    """

    time_now = datetime.now()
    log_values_to_file(LOG_FILES[1], [str(time_now), str(user), str(action)])


def log_values_to_file(log_file, values):
    """
    :param log_file: str
        Path to file to log
    :param values: []
        Array to log
    :return: void
        Append values to log file
    """

    with open(log_file, "a") as logger:
        str_val = ["\"" + str(v) + "\"" for v in values]
        new_row = ",".join(str_val)
        logger.write(new_row)
        logger.write("\n")


def setup_log_files():
    """
    :return: void
        Append headers to log files
    """

    log_values_to_file(
        LOG_FILES[0],
        [
            "time %Y-%m-%d %H:%M:%S",
            "user id",
            "first name",
            "last name"
        ]
    )

    log_values_to_file(
        LOG_FILES[1],
        [
            "time %Y-%m-%d %H:%M:%S",
            "user id",
            "action"
        ]
    )
