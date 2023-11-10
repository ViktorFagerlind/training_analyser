import logging

from garmin_connector import GarminConnector
from training_db import TrainingDb


# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingServer():
    def __init__(self, tdb, connector):
        self.tdb = tdb
        self.connector = connector
        self.tdb.connect('test.db')
        self.tdb.create_activities_table()

    def __del__(self):
        self.tdb.close()

    def update_activities(self):
        nof_added = self.connector.add_activities_to_db(self.tdb)
        if nof_added < 0:
            logger.error('Error from add_activities_from_garmin')
        else:
            print('Added {} activities to dB'.format(nof_added))
            self.tdb.update_fitness_trend()


if __name__ == '__main__':
    server = TrainingServer(TrainingDb(), GarminConnector())
    server.update_activities()
