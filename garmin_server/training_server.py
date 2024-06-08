import logging
import pandas as pd

from concurrent import futures
from garmin_connector import GarminConnector
from training_db import TrainingDb

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
        tdb = TrainingDb()
        tdb.connect(self.db_name)
        tdb.create_activities_table()
        tdb.close()

    def update_activities(self):
        tdb = TrainingDb()
        tdb.connect(self.db_name)
        nof_added = self.connector.add_activities_to_db(tdb)
        if nof_added < 0:
            logger.error('Error from add_activities_from_garmin')
        else:
            print('Added {} activities to dB'.format(nof_added))
            tdb.update_fitness_trend()
        tdb.close()

    def get_fitness_trend(self, timestamp_str=None):
        tdb = TrainingDb()
        tdb.connect(self.db_name)
        trend = tdb.get_fitness_trend(timestamp_str)
        tdb.close()
        return trend

    def UpdateActivities(self, request, context):
        self.update_activities()
        return training_backend_pb2.Empty()

    def GetFitnessTrend(self, request, context):
        trend_df = self.get_fitness_trend()
        trend = training_backend_pb2.FitnessTrend(dates=trend_df.Date.to_list(),
                                                  fatigue=trend_df.Fatigue.to_list(),
                                                  fitness=trend_df.Fitness.to_list(),
                                                  form=trend_df.Form.to_list(),
                                                  tss=trend_df.TSS.to_list())
        return trend


class TrainingServerProxy:
    def __init__(self, stub):
        self.stub = stub

    def update_activities(self):
        self.stub.UpdateActivities(training_backend_pb2.Empty())

    def get_fitness_trend(self):
        protos_fitness_trend = self.stub.GetFitnessTrend(training_backend_pb2.Empty())
        df = pd.DataFrame()

        df['Date'] = list(protos_fitness_trend.dates)
        df['Fatigue'] = list(protos_fitness_trend.fatigue)
        df['Fitness'] = list(protos_fitness_trend.fitness)
        df['Form'] = list(protos_fitness_trend.form)
        df['TSS'] = list(protos_fitness_trend.tss)
        return df


def serve():
    servicer = TrainingTrendsServicer(GarminConnector())

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    training_backend_pb2_grpc.add_TrainingTrendsServicer_to_server(servicer, server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
