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


from datetime import datetime


def get_time_now():
    """
    :return: string
        yyyy-mm-dd hh:mm
    """

    time_now = datetime.now()
    out = str(time_now.year) + "-" + str(time_now.month) + "-" + str(time_now.day)  # add date
    out += " " + str(time_now.hour) + ":" + str(time_now.minute) + ":" + str(time_now.second)  # add hour
    return out
