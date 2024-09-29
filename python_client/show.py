import logging
from training_server_proxy import TrainingServerProxy
import grpc

import sys
import argparse
from plots import plot_fitness_trend, plot_garmin_trend, plot_activities

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    if not len(sys.argv) > 1:
        print('Without arguments, nothing will be shown :)')
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-ft', '--fitness_trend', action='store_true')
    parser.add_argument('-gt', '--garmin_trend', action='store_true')
    parser.add_argument('-hrt', '--heartrate_trend', action='store_true')
    args = parser.parse_args()

    with grpc.insecure_channel("localhost:50051") as channel:
        server = TrainingServerProxy(channel)

        server.update_data()

        if args.fitness_trend:
            fitness_trend_df = server.get_fitness_trend('FITNESS_TREND')
            raw_trend_data_df = server.get_raw_trend_data()
            print(fitness_trend_df.to_string())
            print(raw_trend_data_df.to_string())
            fig = plot_fitness_trend(fitness_trend_df, raw_trend_data_df, '2022-09-10')

        if args.garmin_trend:
            fitness_trend_df = server.get_fitness_trend('GARMIN_TREND')
            raw_trend_data_df = server.get_raw_trend_data()
            print(fitness_trend_df.to_string())
            print(raw_trend_data_df.to_string())
            fig = plot_garmin_trend(fitness_trend_df, raw_trend_data_df, '2022-09-10')

        if args.heartrate_trend:
            activities_df = server.get_activities()
            raw_trend_data_df = server.get_raw_trend_data()
            print(activities_df.to_string())
            fig = plot_activities(activities_df, raw_trend_data_df, '2022-09-10')

        fig.show()