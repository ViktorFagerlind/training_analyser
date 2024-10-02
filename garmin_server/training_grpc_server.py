import logging
import pandas as pd

from concurrent import futures
from garmin_connector import GarminConnector
from training_sql_db import TrainingSqlDb
from algorithms import get_fitness_trends

import grpc
import training_backend_pb2
import training_backend_pb2_grpc


# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingTrendsServicer(training_backend_pb2_grpc.TrainingTrendsServicer):
    def __init__(self, connector):
        self.db_name = 'test.db'
        self.connector = connector
        tdb = TrainingSqlDb()
        tdb.connect(self.db_name)
        tdb.create_activities_table()
        tdb.create_raw_trend_data_table()
        tdb.close()

    def update_data(self):
        tdb = TrainingSqlDb()
        tdb.connect(self.db_name)
        nof_added = self.connector.add_activities_to_db(tdb)
        if nof_added < 0:
            logger.error('Error from add_activities_from_garmin')
        else:
            print('Added {} activities to dB'.format(nof_added))
            df_activities = self.get_activities()
            trends = get_fitness_trends(df_activities)
            for trend in trends:
                tdb.save_fitness_trend(trend[0], trend[1])

        nof_added = self.connector.add_raw_trend_data_to_db(tdb)
        print('Added {} raw trend entries to dB'.format(nof_added))

        tdb.close()

    def get_fitness_trend(self, trend_name, timestamp_str=None):
        tdb = TrainingSqlDb()
        tdb.connect(self.db_name)
        trend = tdb.get_fitness_trend(trend_name=trend_name, timestamp_str=timestamp_str)
        tdb.close()
        return trend

    def get_raw_trend_data(self, timestamp_str=None):
        tdb = TrainingSqlDb()
        tdb.connect(self.db_name)
        raw_trend_data = tdb.get_raw_trend_data(timestamp_str)
        tdb.close()
        return raw_trend_data

    def get_activities(self, timestamp_str=None):
        tdb = TrainingSqlDb()
        tdb.connect(self.db_name)
        df_activities = tdb.get_df_activities(timestamp_str)
        tdb.close()
        return df_activities

    def UpdateData(self, request, context):
        self.update_data()
        print('Updated activities and fitness trend.')
        return training_backend_pb2.Empty()

    def GetFitnessTrend(self, request, context):
        trend_df = self.get_fitness_trend(request.name)
        trend = training_backend_pb2.FitnessTrend(dates=trend_df.Date.to_list(),
                                                  fatigue=trend_df.Fatigue.to_list(),
                                                  fitness=trend_df.Fitness.to_list(),
                                                  form=trend_df.Form.to_list(),
                                                  tss=trend_df.TSS.to_list())
        return trend

    def GetRawTrendData(self, request, context):
        df_raw_trend_data = self.get_raw_trend_data()
        pd_raw_trend_data = training_backend_pb2.RawTrendData(dates=df_raw_trend_data.Date.to_list(),
                                                              vo2max=df_raw_trend_data.VO2MAX.to_list())
        return pd_raw_trend_data

    def GetActivities(self, request, context):
        df_activities = self.get_activities()

        pd_activities = training_backend_pb2.Activities(id=df_activities.id.to_list(),
                                                        name=['No name' if v is None else v for v in df_activities.name.to_list()],
                                                        date_time=df_activities['start_time'].to_list(),
                                                        average_hr=[0 if v is None else v for v in df_activities.average_hr.to_list()],
                                                        max_hr=[0 if v is None else v for v in df_activities.max_hr.to_list()],
                                                        avg_power=[0 if v is None else v for v in df_activities.avg_power.to_list()],
                                                        norm_power=[0 if v is None else v for v in df_activities.norm_power.to_list()],
                                                        training_load=[0 if v is None else v for v in df_activities.training_load.to_list()],
                                                        training_stress_score=[0 if v is None else v for v in df_activities.training_stress_score.to_list()],
                                                        duration=[0 if v is None else v for v in df_activities.duration.to_list()],
                                                        vo2max=[0 if v is None else v for v in df_activities.vo2max.to_list()]
                                                        )
        return pd_activities


def serve():
    servicer = TrainingTrendsServicer(GarminConnector())

    servicer.update_data()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    training_backend_pb2_grpc.add_TrainingTrendsServicer_to_server(servicer, server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
