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

import pytz

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
        latest_trend_data = tdb.get_latest_raw_trend_data_entry_time()
        start_date = datetime(latest_trend_data.year, latest_trend_data.month, latest_trend_data.day) if latest_trend_data is not None else datetime(2022, 1, 1)
        # Calculate the number of days between today and the specific date
        num_days = (today - start_date).days
        for i in range(num_days):
            # Calculate the date for the current day
            date = today - timedelta(days=i)
            datestr = date.strftime('%Y-%m-%d')
            print("get data from " + datestr)

            max_metrics_data = self.api.get_max_metrics(cdate=datestr)
            stats_data = self.api.get_stats(cdate=datestr)
            # resting_hr_data = self.api.get_rhr_day(cdate=datestr)
            # training_status_data = self.api.get_training_status(cdate=datestr)

            try:
                vo2max = max_metrics_data[0]['cycling']['vo2MaxPreciseValue']
                resting_hr = stats_data['restingHeartRate']

                tdb.add_raw_trend_data(pytz.UTC.localize(date), vo2max, resting_hr)
                print('added row {}'.format((date, vo2max, resting_hr)))
                nof_added = nof_added + 1
            except (KeyError, IndexError, TypeError) as err:
                print(err)

        return nof_added

    def add_activities_to_db(self, tdb, max_to_add=-1):
        nof_activities_added = 0
        newer_than = tdb.get_latest_activity_entry_time()

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
        limit = 100 if max_to_add <= 0 or max_to_add >= 100 else max_to_add
        while max_to_add <= 0 or nof_activities_added < max_to_add:
            activities = self.api.get_activities(start=start, limit=limit)
            if not activities:
                return nof_activities_added

            for a in activities:
                activityType = a['activityType']['typeKey']
                if ('cycling' in activityType or 'biking' in activityType):
                    activity_time = datetime.strptime(a['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                    activity_time_utc = pytz.UTC.localize(activity_time)
                    if newer_than is not None and activity_time_utc < newer_than:
                        return nof_activities_added

                    if tdb.check_if_activity_exists(a[db_to_garmin['id']]):
                        continue

                    activity = {}
                    for k in db_to_garmin.keys():
                        activity[k] = a.get(db_to_garmin[k])

                    tdb.add_activity(activity)
                    nof_activities_added = nof_activities_added + 1
                    print('added row {}'.format(activity))
            start = start + limit
