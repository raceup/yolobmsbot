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

import httplib2
from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCRIPT_DIRECTORY = os.path.dirname(__file__)  # path to directory of python script running

# app settings
APP_NAME = "Bms Remote Monitor"
APP_WEBSITE = "https://sites.google.com/view/raceupbms/home"
APP_ORGANIZATION_WEBSITE = "www.raceup.it"
OAUTH_PATH = os.path.join(os.path.dirname(SCRIPT_DIRECTORY), ".user_credentials")  # credentials folder


class GoogleApiOAuth(object):
    def __init__(self, scope, app_secrets_path, user_credentials_path):
        """
        :param scope: string
            scope of api
        :param app_secrets_path: string
            path to app secrets
        :param user_credentials_path: string
            path to user credentials
        """

        object.__init__(self)

        self.scope = str(scope)
        self.app_secrets = str(app_secrets_path)
        self.user_credentials = str(user_credentials_path)
        self.store = Storage(user_credentials_path)

    def get_new_user_credentials(self):
        """
        :return: credentials
            New user credentials file upon user prompt
        """

        flow = client.flow_from_clientsecrets(self.app_secrets, self.scope)  # perform OAuth2.0 authorization flow.
        flow.user_agent = APP_NAME
        return tools.run_flow(flow, self.store)

    def get_user_credentials(self):
        """
        :return: string
            User credentials created via OAuth
        """

        if not os.path.exists(os.path.dirname(self.user_credentials)):  # create path to user credentials if needed
            os.makedirs(os.path.dirname(self.user_credentials))

        credentials = self.store.get()  # retrieve credentials
        if not credentials or credentials.invalid:  # user credentials are to be updated
            self.get_new_user_credentials()  # get new user credentials
            credentials = self.store.get()  # retrieve new credentials

        return credentials

    @staticmethod
    def authenticate(credentials):
        """
        :param credentials: string
            User authentication code created via OAuth
        :return: http
            Http authenticated credentials
        """

        http = httplib2.Http()
        credentials.authorize(http)
        return http

    def get_driver(self, name, version):
        """
        :param name: string
            Name of driver
        :param version: string
            Version of driver
        :return: api driver
            Authenticates and creates new API driver to perform scope stuff
        """

        user_credentials = self.get_user_credentials()  # get credentials
        return discovery.build(name, version, http=self.authenticate(user_credentials))  # get sheets driver


class GMailApiOAuth(GoogleApiOAuth):
    def __init__(self):
        GoogleApiOAuth.__init__(
            self,
            "https://www.googleapis.com/auth/gmail.send",  # scope
            os.path.join(OAUTH_PATH, "gmail", "gmail_secrets.json"),  # app secrets
            os.path.join(OAUTH_PATH, "gmail", "gmail.json"),  # user credential
        )

    def create_driver(self):
        """
        :return: driver
            Gmail API driver
        """

        return super().get_driver("gmail", "v1")


class GSheetsApiOAuth(GoogleApiOAuth):
    def __init__(self):
        GoogleApiOAuth.__init__(
            self,
            "https://www.googleapis.com/auth/spreadsheets",  # scope
            os.path.join(OAUTH_PATH, "gsheets", "gsheets_secrets.json"),  # app secrets
            os.path.join(OAUTH_PATH, "gsheets", "gsheets.json"),  # user credential
        )

    def create_driver(self):
        """
        :return: driver
            GSheets API driver
        """

        return super().get_driver("sheets", "v4")


def create_gmail_driver():
    """
    :return: gmail driver
        Authenticates and creates new Google Mail driver to perform GMail stuff
    """

    return GMailApiOAuth().create_driver()


def create_gdrive_driver():
    """
    :return: gdrive driver
        Authenticates and creates new Google Drive driver to perform GDrive stuff
    """

    return GSheetsApiOAuth().create_driver()
