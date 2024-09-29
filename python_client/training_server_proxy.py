import sys
from pathlib import Path

server_path = Path(__file__).parent.parent / 'garmin_server'
sys.path.append(str(server_path))

import training_backend_pb2
import training_backend_pb2_grpc
import pandas as pd

class TrainingServerProxy:
    def __init__(self, channel):
        stub = training_backend_pb2_grpc.TrainingTrendsStub(channel)
        self.stub = stub

    def update_data(self):
        self.stub.UpdateData(training_backend_pb2.Empty())

    def get_fitness_trend(self, trend_name):
        name_arg = training_backend_pb2.Name()
        name_arg.name = trend_name
        protos_fitness_trend = self.stub.GetFitnessTrend(name_arg)
        df = pd.DataFrame()

        df['Date'] = list(protos_fitness_trend.dates)
        df['Fatigue'] = list(protos_fitness_trend.fatigue)
        df['Fitness'] = list(protos_fitness_trend.fitness)
        df['Form'] = list(protos_fitness_trend.form)
        df['TSS'] = list(protos_fitness_trend.tss)
        return df

    def get_raw_trend_data(self):
        protos_raw_trend_data = self.stub.GetRawTrendData(training_backend_pb2.Empty())
        df = pd.DataFrame()
        df['dates'] = list(protos_raw_trend_data.dates)
        df['vo2max'] = list(protos_raw_trend_data.vo2max)
        return df

    def get_activities(self):
        protos_activities = self.stub.GetActivities(training_backend_pb2.Empty())
        df = pd.DataFrame()
        df['id'] = list(protos_activities.id)
        df['name'] = list(protos_activities.name)
        df['date_time'] = list(protos_activities.date_time)
        df['average_hr'] = list(protos_activities.average_hr)
        df['max_hr'] = list(protos_activities.max_hr)
        df['avg_power'] = list(protos_activities.avg_power)
        df['norm_power'] = list(protos_activities.norm_power)
        df['training_load'] = list(protos_activities.training_load)
        df['training_stress_score'] = list(protos_activities.training_stress_score)
        df['duration'] = list(protos_activities.duration)
        df['vo2max'] = list(protos_activities.vo2max)
        return df
