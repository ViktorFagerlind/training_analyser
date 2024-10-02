import firebase_admin
import pandas as pd

from datetime import datetime
from firebase_admin import credentials, firestore

import pytz
utc = pytz.UTC


def delete_collection(coll_ref, batch_size):
    if batch_size == 0:
        return

    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.get().to_dict()}")
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


def collection_to_df(coll_ref, timestamp_str):
    if timestamp_str is not None:
        time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        docs = coll_ref.where('start_time', '>', time).order_by('start_time').stream()
    else:
        docs = coll_ref.order_by('start_time').stream()

    items = list(map(lambda x: {**x.to_dict(), 'id': x.id}, docs))
    df = pd.DataFrame(items)
    df.set_index('id', inplace=True)
    return df


class TrainingFsDb:
    def __init__(self):
        self.db = None

    def connect(self, db_file):
        cred = credentials.Certificate(db_file)
        firebase_admin.initialize_app(cred)

        self.db = firestore.client()

    def close(self):
        pass

    def check_if_activity_exists(self, id):
        return self.db.collection('activities').document(str(id)).get().exists

    def add_raw_trend_data(self, date, vo2max, resting_hr):
        trend = {
            'date': date,
            'vo2max': vo2max,
            'resting_hr': resting_hr
        }
        id = date.strftime('%Y-%m-%d')

        doc_ref = self.db.collection('raw_trend').document(id)
        doc_ref.set(trend)


    def save_fitness_trend(self, name, df_trend):
        to_save = {}

        for col in df_trend:
            to_save[col] = df_trend[col].tolist() if col != 'Date' else [str(date) for date in df_trend[col].tolist()]

        doc_ref = self.db.collection('fitness_trend').document(name)
        doc_ref.set(to_save)

    def get_fitness_trend(self, trend_name='FITNESS_TREND', timestamp_str=None):
        trend_dict = self.db.collection('fitness_trend').document(trend_name).get().to_dict()
        trend_df = pd.DataFrame(trend_dict)
        return trend_df

    def get_latest_raw_trend_data_entry_time(self):
        latest_query = self.db.collection('raw_trend').order_by('datetime', direction=firestore.Query.DESCENDING).limit(1)
        latest = latest_query.get()

        if not latest:
            return None

        return latest[0].to_dict()['start_time']

    def get_raw_trend_data(self, timestamp_str=None):
        pass


    def get_latest_activity_entry_time(self):
        latest_query = self.db.collection('activities').order_by('start_time', direction=firestore.Query.DESCENDING).limit(1)
        latest = latest_query.get()

        if not latest:
            return None

        return latest[0].to_dict()['start_time']

    def add_activity(self, activity):
        id = activity['id']
        del activity['id']
        activity['start_time'] = datetime.strptime(activity['start_time'], '%Y-%m-%d %H:%M:%S')

        doc_ref = self.db.collection('activities').document(str(id))
        doc_ref.set(activity)

    def get_df_activities(self, timestamp_str=None):
        return collection_to_df(self.db.collection('activities'), timestamp_str=timestamp_str)

    def delete(self, collection_name):
        delete_collection(coll_ref=self.db.collection(collection_name), batch_size=100)
