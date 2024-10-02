import sys
import argparse
import logging

from concurrent import futures
from garmin_connector import GarminConnector
from training_fs_db import TrainingFsDb
from algorithms import get_fitness_trends

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect():
    tdb = TrainingFsDb()
    tdb.connect('trainingtrends-private-key.json')
    return tdb


def delete_collection(collection_name):
    print('deleting activities')
    tdb = connect()
    tdb.delete(collection_name)
    tdb.close()


def update_data():
    print('updating data')

    tdb = connect()
    gc = GarminConnector()

    print('add activities to db')
    nof_added = gc.add_activities_to_db(tdb)

    if nof_added < 0:
        logger.error('Error from add_activities_from_garmin')
    else:
        print('Added {} activities to dB'.format(nof_added))
        if nof_added != 0:
            print('Recalculating and storing fitness trends')
            df_activities = tdb.get_df_activities()
            trends = get_fitness_trends(df_activities)
            for trend in trends:
                tdb.save_fitness_trend(trend[0], trend[1])

    nof_added = gc.add_raw_trend_data_to_db(tdb)
    print('Added {} raw trend entries to dB'.format(nof_added))

    tdb.close()


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        update_data()
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--update', action='store_true')
    parser.add_argument('-da', '--delete_activities', action='store_true')
    parser.add_argument('-dft', '--delete_fitness_trend', action='store_true')
    parser.add_argument('-drt', '--delete_raw_trend', action='store_true')
    args = parser.parse_args()

    if args.update:
        update_data()

    if args.delete_activities:
        delete_collection('activities')
    if args.delete_fitness_trend:
        delete_collection('fitness_trend')
    if args.delete_raw_trend:
        delete_collection('raw_trend')

