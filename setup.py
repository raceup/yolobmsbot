# !/usr/bin/python3
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


from setuptools import setup, find_packages


DESCRIPTION = \
    "Raceup Ed Bms Telegram bot\n\n\
    Receive updates about the Raceup remote bms.\n\
    \n\
    About\n\n\
    Read the README.md file where you can find all information.\n\
    \n\
    License: Apache License Version 2.0, January 2004"


setup(
    name="yolobmsbot",
    version="0.1",
    author="sirfoga",
    author_email="sirfoga@protonmail.com",
    description="Receive updates about the Raceup remote bms.",
    long_description=DESCRIPTION,
    license="Apache License, Version 2.0",
    keywords="library scratch maths",
    url="https://bitbucket.org/raceuped/bms-telegram-bot",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "oauth2client",
        "google-api-python-client",
        "apiclient",
        "inflect",
        "httplib2",
        "python-telegram-bot"
    ],
    test_suite="tests"
)
