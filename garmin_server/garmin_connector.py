'''
export EMAIL=<your garmin email>
export PASSWORD=<your garmin password>
'''

import logging
import os
import requests
from connector import ConnectorInterface

from getpass import getpass
from datetime import datetime
from garth.exc import GarthHTTPError
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError
)

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_info_item(d, itemname):
    print('  {}: {}'.format(itemname.ljust(20), d[itemname]))


class GarminConnector(ConnectorInterface):
    def __init__(self):
        # Load environment variables if defined
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"

    def __get_credentials(self):
        """Get user credentials."""

        self.email = input("Login e-mail: ")
        self.password = getpass("Enter password: ")

        return self.email, self.password

    def __init_api(self, email, password):
        """Initialize Garmin API with your credentials."""

        try:
            print(
                f"Trying to login to Garmin Connect using token data from '{self.tokenstore}'...\n"
            )
            garmin = Garmin()
            garmin.login(self.tokenstore)
        except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
            # Session is expired. You'll need to log in again
            print(
                "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
                f"They will be stored in '{self.tokenstore}' for future use.\n"
            )
            try:
                # Ask for credentials if not set as environment variables
                if not email or not password:
                    email, password = self.__get_credentials()

                garmin = Garmin(email, password)
                garmin.login()
                # Save tokens for next login
                garmin.garth.dump(self.tokenstore)

            except (
                    FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError,
                    requests.exceptions.HTTPError) as err:
                logger.error(err)
                return None

        return garmin

    def add_activities_to_db(self, tdb):
        nof_activities_added = 0
        newer_than = tdb.get_latest_activity_entry()

        api = self.__init_api(self.email, self.password)

        if not api:
            logger.error('Could not connect to Garmin')
            return -1

        db_to_garmin = {'id': 'activityId',
                        'name': 'activityName',
                        'start_time': 'startTimeLocal',
                        'average_hr': 'averageHR',
                        'max_hr': 'maxHR',
                        'avg_power': 'avgPower',
                        'norm_power': 'normPower',
                        'training_load': 'activityTrainingLoad',
                        'training_stress_score': 'trainingStressScore'}

        start = 0
        limit = 100
        while True:
            activities = api.get_activities(start=start, limit=limit)
            if not activities:
                return nof_activities_added

            for a in activities:
                activityType = a['activityType']['typeKey']
                if ('cycling' in activityType or 'biking' in activityType):
                    activity_time = datetime.strptime(a['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                    if newer_than is not None and activity_time < newer_than:
                        return nof_activities_added

                    if tdb.check_if_activity_exists(a[db_to_garmin['id']]):
                        continue

                    activity = [a.get(v) for v in db_to_garmin.values()]
                    '''
                    activity = []
                    for v in db_to_garmin.values():
                        value = a.get(v)
                        if value:
                            activity.append(value)
                        else:
                            activity.append(None)
                            print("Could not find " + str(v))
                    '''

                    tdb.add_activity(tuple(activity))
                    nof_activities_added = nof_activities_added + 1
                    print('added row {}'.format(activity))

            start = start + limit
