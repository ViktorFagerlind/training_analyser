import sqlite3
import logging
import pandas as pd

from datetime import datetime, date

import pytz

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


def get_db_get_latest_entry_time(conn, table_name, time_column, time_format=TimeEntryType.TimeStamp):
    try:
        c = conn.cursor()
        c.execute('SELECT {} FROM {} ORDER BY {} DESC LIMIT 1'.format(time_column, table_name, time_column))

        data = c.fetchone()
        if data is None:
            return None

        entry_time = datetime.strptime(data[0], '%Y-%m-%d %H:%M:%S' if time_format==TimeEntryType.TimeStamp else '%Y-%m-%d')
        return pytz.UTC.localize(entry_time)

    except sqlite3.Error as e:
        logger.error(e)


class TrainingSqlDb:
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

    def create_raw_trend_data_table(self):
        create_session_table_sql = '''CREATE TABLE IF NOT EXISTS RAW_TREND_DATA
                              (Date                     DATE   PRIMARY KEY NOT NULL,
                               VO2MAX                   REAL,
                               RESTING_HR               REAL);'''

        create_db_table(self.db_connection, create_session_table_sql)

    def add_raw_trend_data(self, date, vo2max, resting_hr):
        add_raw_trend_data_sql = '''INSERT INTO RAW_TREND_DATA(Date, VO2MAX, RESTING_HR) VALUES(?,?,?)'''
        add_db_row(self.db_connection, add_raw_trend_data_sql, (date.strftime('%Y-%m-%d'), vo2max, resting_hr))

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
                               training_stress_score    REAL,
                               duration                 REAL,
                               vo2max                   REAL);'''

        create_db_table(self.db_connection, create_session_table_sql)

    def save_fitness_trend(self, name, df_trend):
        df_trend.to_sql(name, self.db_connection, if_exists='replace', index=False)

    def get_fitness_trend(self, trend_name='FITNESS_TREND', timestamp_str=None):
        if timestamp_str is None:
            return pd.read_sql_query('SELECT * FROM ' + trend_name, self.db_connection)
        else:
            return pd.read_sql_query(
                'SELECT * FROM ' + trend_name + ' WHERE Date > "{}" ORDER BY Date'.format(timestamp_str),
                self.db_connection)

    def get_latest_raw_trend_data_entry_time(self):
        latest_entry_timestamp = get_db_get_latest_entry_time(self.db_connection, 'RAW_TREND_DATA', 'Date',
                                                              time_format=TimeEntryType.Date)
        return latest_entry_timestamp.date() if latest_entry_timestamp is not None else None

    def get_raw_trend_data(self, timestamp_str=None):
        if timestamp_str is None:
            return pd.read_sql_query('SELECT * FROM RAW_TREND_DATA ORDER BY Date', self.db_connection)
        else:
            return pd.read_sql_query(
                'SELECT * FROM RAW_TREND_DATA WHERE Date > "{}" ORDER BY Date'.format(timestamp_str),
                self.db_connection)

    def get_latest_activity_entry_time(self):
        return get_db_get_latest_entry_time(self.db_connection, 'ACTIVITIES', 'start_time')

    def add_activity(self, activity):
        activity_tuple = tuple([v for v in activity.values()])
        add_activity_sql = '''INSERT INTO ACTIVITIES(ID, name, start_time, average_hr, max_hr, avg_power, norm_power, 
                                                     training_load, training_stress_score, duration, vo2max)
                                                     VALUES(?,?,?,?,?,?,?,?,?,?,?)'''
        add_db_row(self.db_connection, add_activity_sql, activity_tuple)

    def get_df_activities(self, timestamp_str=None):
        if timestamp_str is None:
            return pd.read_sql_query('SELECT * FROM ACTIVITIES ORDER BY start_time', self.db_connection)
        else:
            return pd.read_sql_query(
                'SELECT * FROM ACTIVITIES WHERE start_time > "{}" ORDER BY start_time'.format(timestamp_str), self.db_connection)


