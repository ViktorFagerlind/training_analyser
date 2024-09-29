import pandas as pd
from enum import IntEnum
from datetime import timedelta, date
import math

future_trend_days = timedelta(days=14)

def get_day_tss(df, date):
    stresses = df[df['date'] == date]['training_stress_score']
    tss = 0
    for s in stresses:
        if not math.isnan(s):
            tss = tss + s
    return tss


def get_day_load(df, date):
    loads = df[df['date'] == date]['training_load']
    load = 0
    for l in loads:
        if not math.isnan(l):
            load = load + l
    return load


def get_fitness_trends(df_activities):
    df_activities['date'] = pd.to_datetime(df_activities['start_time']).dt.date

    date_series = []

    class Load(IntEnum):
        TSS = 0
        GARMIN_LOAD = 1

    fatigue_series = [[], []]
    fitness_series = [[], []]
    form_series = [[], []]
    load_series = [[], []]
    fatigue = [0, 0]
    fitness = [0, 0]
    form = [0, 0]

    current_date = min(df_activities['date'])
    today = date.today()
    day = timedelta(days=1)
    while current_date <= today + future_trend_days:
        load = [get_day_tss(df_activities, current_date),
                get_day_load(df_activities, current_date)]
        for l in Load:
            load_series[l].append(load[l])
            fatigue[l] = fatigue[l] + (load[l] - fatigue[l]) * (1 - math.exp(-1.0 / 7.0))
            fitness[l] = fitness[l] + (load[l] - fitness[l]) * (1 - math.exp(-1.0 / 42.0))
            fatigue_series[l].append(fatigue[l])
            fitness_series[l].append(fitness[l])
            form[l] = fitness[l] - fatigue[l]
            form_series[l].append(form[l])
        date_series.append(current_date)
        current_date = current_date + day

    db_names = ['FITNESS_TREND', 'GARMIN_TREND']

    df_trends = []

    for l in Load:
        data = {'Date': date_series,
                'Fatigue': fatigue_series[l],
                'Fitness': fitness_series[l],
                'Form': form_series[l],
                'TSS': load_series[l]}
        df_trends.append((db_names[l], pd.DataFrame(data)))

    return df_trends
