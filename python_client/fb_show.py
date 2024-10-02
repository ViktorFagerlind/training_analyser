import logging

import sys
import argparse
from plots import plot_fitness_trend, plot_garmin_trend, plot_activities

sys.path.append('../parentdirectory')
from training_fs_db import TrainingFsDb


# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect():
    tdb = TrainingFsDb()
    tdb.connect('../garmin_server/trainingtrends-private-key.json')
    return tdb


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        print('Without arguments, nothing will be shown :)')
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-ft', '--fitness_trend', action='store_true')
    parser.add_argument('-gt', '--garmin_trend', action='store_true')
    parser.add_argument('-hrt', '--heartrate_trend', action='store_true')
    args = parser.parse_args()

    tdb = connect()

    fig = None

    if args.fitness_trend:
        fitness_trend_df = tdb.get_fitness_trend('FITNESS_TREND')
        raw_trend_data_df = tdb.get_raw_trend_data()
        print(fitness_trend_df.to_string())
        print(raw_trend_data_df.to_string())
        fig = plot_fitness_trend(fitness_trend_df, raw_trend_data_df, '2022-09-10')

    if args.garmin_trend:
        fitness_trend_df = tdb.get_fitness_trend('GARMIN_TREND')
        raw_trend_data_df = tdb.get_raw_trend_data()
        print(fitness_trend_df.to_string())
        print(raw_trend_data_df.to_string())
        fig = plot_garmin_trend(fitness_trend_df, raw_trend_data_df, '2022-09-10')

    if args.heartrate_trend:
        activities_df = tdb.get_df_activities()
        raw_trend_data_df = tdb.get_raw_trend_data()
        print(activities_df.to_string())
        fig = plot_activities(activities_df, raw_trend_data_df, '2022-09-10')

    if fig is not None:
        fig.show()
