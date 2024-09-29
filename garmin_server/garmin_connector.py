'''
export EMAIL=<your garmin email>
export PASSWORD=<your garmin password>
'''

import logging
import os
import requests
from connector import ConnectorInterface

from getpass import getpass
from datetime import datetime, timedelta
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
        self.api = self.__init_api(self.email, self.password)

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

    def add_raw_trend_data_to_db(self, tdb):
        """ Adds all the vo2max up to todays date to the database """
        nof_added = 0

        if not self.api:
            logger.error('Could not connect to Garmin')
            return -1

        # Get today's date
        today = datetime.today()
        # Define the specific date you want to loop until
        latest_trend_data = tdb.get_latest_raw_trend_data_entry()
        start_date = datetime(latest_trend_data.year, latest_trend_data.month, latest_trend_data.day) if latest_trend_data is not None else datetime(2017, 1, 1)
        # Calculate the number of days between today and the specific date
        num_days = (today - start_date).days
        # Loop over the number of days in 4 years
        for i in range(num_days):
            # Calculate the date for the current day
            date = today - timedelta(days=i)
            datestr = date.strftime('%Y-%m-%d')

            max_metrics_data = self.api.get_max_metrics(cdate=datestr)
            stats_data = self.api.get_stats(cdate=datestr)
            # resting_hr_data = self.api.get_rhr_day(cdate=datestr)
            # training_status_data = self.api.get_training_status(cdate=datestr)

            try:
                vo2max = max_metrics_data[0]['cycling']['vo2MaxPreciseValue']
                resting_hr = stats_data['restingHeartRate']

                tdb.add_raw_trend_data(date, vo2max, resting_hr)
                print('added row {}'.format((date, vo2max, resting_hr)))
                nof_added = nof_added + 1
            except (KeyError, IndexError, TypeError) as _:
                pass

        return nof_added

    def add_activities_to_db(self, tdb):
        nof_activities_added = 0
        newer_than = tdb.get_latest_activity_entry()

        if not self.api:
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
                        'training_stress_score': 'trainingStressScore',
                        'duration': 'duration',
                        'vo2max': 'vO2MaxValue'}

        start = 0
        limit = 100
        while True:
            activities = self.api.get_activities(start=start, limit=limit)
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

                    tdb.add_activity(tuple(activity))
                    nof_activities_added = nof_activities_added + 1
                    print('added row {}'.format(activity))

            start = start + limit
