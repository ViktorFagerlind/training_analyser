import sqlite3
import logging
import pandas as pd
import math

from datetime import datetime, timedelta, date
from enum import Enum

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_db_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        logger.error(e)

    return conn


def create_db_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        logger.error(e)


def get_db_table_column_names(conn, table_name):
    try:
        c = conn.cursor()
        c.execute('select * from {}'.format(table_name))
        return [description[0] for description in c.description]
    except sqlite3.Error as e:
        logger.error(e)


def add_db_row(conn, sql, tuple):
    cur = conn.cursor()
    cur.execute(sql, tuple)
    conn.commit()

    return cur.lastrowid


def print_info_db_table(conn, table_name):
    try:
        print(pd.read_sql_query('SELECT * FROM ' + table_name, conn))
    except sqlite3.Error as e:
        logger.error(e)


class TimeEntryType(Enum):
    TimeStamp = 1
    Date = 2


def get_db_get_latest_entry(conn, table_name, time_column, time_format=TimeEntryType.TimeStamp):
    try:
        c = conn.cursor()
        c.execute('SELECT {} FROM {} ORDER BY {} DESC LIMIT 1'.format(time_column, table_name, time_column))

        data = c.fetchone()
        return None if data is None else datetime.strptime(data[0],
                                                           '%Y-%m-%d %H:%M:%S' if time_format==TimeEntryType.TimeStamp
                                                           else '%Y-%m-%d')
    except sqlite3.Error as e:
        logger.error(e)


class TrainingDb:
    future_trend_days = timedelta(days=14)

    def __init__(self):
        self.db_connection = None

    def connect(self, db_file):
        self.db_connection = create_db_connection(db_file)
        if self.db_connection is None:
            logger.error("Error! cannot create the database connection.")

        return self.db_connection

    def close(self):
        self.db_connection.close()

    def check_if_activity_exists(self, id):
        try:
            c = self.db_connection.cursor()
            c.execute("SELECT rowid FROM ACTIVITIES WHERE ID = {}".format(id))
            data = c.fetchone()
            return data is not None
        except sqlite3.Error as e:
            logger.error(e)

    def create_activities_table(self):
        create_session_table_sql = '''CREATE TABLE IF NOT EXISTS ACTIVITIES
                              (id                       INT   PRIMARY KEY NOT NULL,
                               name                     TEXT,
                               start_time               TIMESTAMP  NOT NULL,
                               average_hr               REAL,
                               max_hr                   REAL,
                               avg_power                REAL,
                               norm_power               REAL,
                               training_load            REAL,
                               training_stress_score    REAL);'''

        create_db_table(self.db_connection, create_session_table_sql)

    @staticmethod
    def get_day_tss(df, date):
        stresses = df[df['date'] == date]['training_stress_score']
        tss = 0
        for s in stresses:
            if not math.isnan(s):
                tss = tss + s
        return tss

    def update_fitness_trend(self):
        df_activities = self.get_activities()
        df_activities['date'] = pd.to_datetime(df_activities['start_time']).dt.date

        date_series = []
        fatigue_series = []
        fitness_series = []
        form_series = []
        tss_series = []
        fatigue = 0
        fitness = 0
        form = 0
        current_date = min(df_activities['date'])
        today = date.today()
        day = timedelta(days=1)
        while current_date <= today + self.future_trend_days:
            tss = TrainingDb.get_day_tss(df_activities, current_date)
            tss_series.append(tss)
            fatigue = fatigue + (tss - fatigue) * (1 - math.exp(-1.0 / 7.0))
            fitness = fitness + (tss - fitness) * (1 - math.exp(-1.0 / 42.0))
            fatigue_series.append(fatigue)
            fitness_series.append(fitness)
            form_series.append(form)
            form = fitness - fatigue
            date_series.append(current_date)
            current_date = current_date + day

        data = {'Date': date_series,
                'Fatigue': fatigue_series,
                'Fitness': fitness_series,
                'Form': form_series,
                'TSS': tss_series}

        df_fitness_trend = pd.DataFrame(data)

        df_fitness_trend.to_sql('FITNESS_TREND', self.db_connection, if_exists='replace', index=False)

    def get_fitness_trend(self, timestamp_str=None):
        latest_fitness_entry = self.get_latest_fitness_trend_entry()
        if latest_fitness_entry is None or date.today() > latest_fitness_entry:
            print('Updating fitness trend')
            self.update_fitness_trend()

        if timestamp_str is None:
            return pd.read_sql_query('SELECT * FROM FITNESS_TREND ORDER BY Date', self.db_connection)
        else:
            return pd.read_sql_query(
                'SELECT * FROM FITNESS_TREND WHERE Date > "{}" ORDER BY Date'.format(timestamp_str),
                self.db_connection)

    def get_latest_fitness_trend_entry(self):
        latest_entry_timestamp = get_db_get_latest_entry(self.db_connection, 'FITNESS_TREND', 'Date',
                                                         time_format=TimeEntryType.Date)
        return latest_entry_timestamp.date() - self.future_trend_days if latest_entry_timestamp is not None else None

    def get_latest_activity_entry(self):
        return get_db_get_latest_entry(self.db_connection, 'ACTIVITIES', 'start_time')

    def add_activity(self, activity):
        add_activity_sql = '''INSERT INTO ACTIVITIES(ID, name, start_time, average_hr, max_hr, avg_power, norm_power, 
                                                     training_load, training_stress_score)
                                                     VALUES(?,?,?,?,?,?,?,?,?)'''
        add_db_row(self.db_connection, add_activity_sql, activity)

    def get_activities(self, timestamp_str=None):
        if timestamp_str is None:
            return pd.read_sql_query('SELECT * FROM ACTIVITIES ORDER BY start_time', self.db_connection)
        else:
            return pd.read_sql_query(
                'SELECT * FROM ACTIVITIES WHERE start_time > "{}" ORDER BY start_time'.format(timestamp_str), self.db_connection)


