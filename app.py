from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import json
import os
import sqlite3
import datetime
import re

BASE_PATH = ''
LOG_PATH = 'app.log'
LOG_LEVEL = logging.DEBUG


app = Flask(__name__)
app.config['SECRET_KEY'] = 'krabby patty recipe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_PATH, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

handler = RotatingFileHandler(os.path.join(BASE_PATH, LOG_PATH), maxBytes=1000000, backupCount=5)
handler.setLevel(LOG_LEVEL)

formatter = logging.Formatter('%(asctime)s - %(pathname)s: line %(lineno)d - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger('werkzeug')
logger.addHandler(handler)
logger.setLevel(LOG_LEVEL)

logger.info('Program Start')


dt_to_re_map = {
        '%Y/%m/%d %H:%M:%S': re.compile('[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}'),
        '%Y-%m-%dT%H:%M:%S': re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}'),
        '%m/%d/%Y %H:%M:%S': re.compile('[0-9]{2}/[0-9]{2}/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}'),
        '%m-%d-%YT%H:%M:%S': re.compile('[0-9]{2}-[0-9]{2}-[0-9]{4}T[0-9]{2}:[0-9]{2}:[0-9]{2}'),
    }


class Restaurant(db.Model):
    query: db.Query  # Just a type hint
    id = db.Column(db.Integer, primary_key=True)
    # TODO make name field not unique and add address field as unique to accommodate dupes
    name = db.Column(db.String(255), unique=True)
    tz = db.Column(db.String(255), server_default='UTC')

    monday_open = db.Column(db.Integer)
    monday_closed = db.Column(db.Integer)

    tuesday_open = db.Column(db.Integer)
    tuesday_closed = db.Column(db.Integer)

    wednesday_open = db.Column(db.Integer)
    wednesday_closed = db.Column(db.Integer)

    thursday_open = db.Column(db.Integer)
    thursday_closed = db.Column(db.Integer)

    friday_open = db.Column(db.Integer)
    friday_closed = db.Column(db.Integer)

    saturday_open = db.Column(db.Integer)
    saturday_closed = db.Column(db.Integer)

    sunday_open = db.Column(db.Integer)
    sunday_closed = db.Column(db.Integer)


class ETL:

    def __init__(self, _db, method='csv'):
        self.db = _db
        self.day_map = {
            'monday': 0, 'mon': 0, 0: 'monday',
            'tuesday': 1, 'tues': 1, 1: 'tuesday',
            'wednesday': 2, 'wed': 2, 2: 'wednesday',
            'thursday': 3, 'thu': 3, 3: 'thursday',
            'friday': 4, 'fri': 4, 4: 'friday',
            'saturday': 5, 'sat': 5, 5: 'saturday',
            'sunday': 6, 'sun': 6, 6: 'sunday'
        }
        self.all_days = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')
        if method == 'csv':
            self.method = self.etl_from_csv
            return
        raise NotImplementedError

    def etl_from_csv(self, filename='restaurants.csv'):
        import pandas
        data = pandas.read_csv(filename)
        for line_no, row in data.iterrows():
            name = row["Restaurant Name"]
            master = {'name': name}
            for ts in row["Hours"].split(' / '):
                master.update(self.standardize_ts(ts))
            existing = Restaurant.query.filter_by(name=name).first()
            # db.session.merge not working :(
            if existing:
                db.session.delete(existing)
                db.session.commit()
            db.session.add(Restaurant(**master))
        db.session.commit()

    def standardize_ts(self, ts_str='Mon-Fri, Sun 11 am - 10:30 pm'):
        """Convert human readable ts into ts object for loading into db"""
        # TODO create regex for faster string parsing, for now we parse slowly for readability as it's a PoC
        ts_str = ts_str.lower()
        parts = ts_str.split(' ')
        days = []
        i = -1
        while i < len(parts):  # loop to get all the days, break when we hit a number
            i += 1
            part = parts[i].replace(',', '')
            try:
                int(part.replace(':', ''))
                break
            except ValueError:
                pass
            if '-' in part:
                day_range = part.split('-')
                for _i in range(self.day_map[day_range[0]], self.day_map[day_range[1]] + 1):
                    days.append(self.day_map[_i])
                continue
            days.append(self.day_map[self.day_map[part]])

        # Because sending 11 am not 11:00 am
        parts[i] = f'{parts[i]}:00' if ':' not in parts[i] else parts[i]
        parts[i + 3] = f'{parts[i + 3]}:00' if ':' not in parts[i + 3] else parts[i + 3]
        _open = int(parts[i].replace(':', '')) if parts[i + 1] == 'am' else int(parts[i].replace(':', '')) + 1200
        # This line checks for 12 am
        parts[i + 3] = f'00{parts[i + 3][2:]}' if parts[i + 3].startswith('12') and parts[i + 4] == 'am' else parts[i + 3]
        _closed = int(parts[i + 3].replace(':', '')) if parts[i + 4] == 'am' else int(parts[i + 3].replace(':', '')) + 1200
        _closed = _closed + 2400 if _closed <= _open else _closed
        obj = {}
        for day in days:
            obj[f'{day}_open'] = _open
            obj[f'{day}_closed'] = _closed
        return obj


def interpret_ts(ts):
    if type(ts) is int:
        return datetime.datetime.fromtimestamp(ts)
    if type(ts) is str:
        for dt_pattern, regex in dt_to_re_map.items():
            if regex.match(ts):
                return datetime.datetime.strptime(ts, dt_pattern)
    return None


app_etl = ETL(db)

# *********************************************************************************************************************
# ******************************************        Basic Endpoints        ********************************************
# *********************************************************************************************************************


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        if 'datetime' not in request.args:
            return json.dumps({'success': False, 'message': '"datetime" parameter is required.'}), 400, {'ContentType': 'application/json'}
        str_ts = request.args['datetime']
    if request.method == 'POST':
        payload = json.loads(request.data)
        if 'datetime' not in payload:
            return json.dumps({'success': False, 'message': '"datetime" tag expected in json payload.'}), 400, {'ContentType': 'application/json'}
        str_ts = payload['datetime']
    dt = interpret_ts(str_ts)
    if not dt:
        return json.dumps({'success': False, 'message': f'Unsupported datetime string format.\nTry one of these: {dt_to_re_map.keys()}'}), \
               400, {'ContentType': 'application/json'}
    attempt_1 = (app_etl.day_map[dt.weekday()], int(dt.strftime('%H%M')))
    attempt_2 = (app_etl.day_map[dt.weekday() - 1], int(dt.strftime('%H%M')) + 2400)
    results = set(Restaurant.query.filter(getattr(Restaurant, f'{attempt_1[0]}_open') <= attempt_1[1],
                                          getattr(Restaurant, f'{attempt_1[0]}_closed') >= attempt_1[1]).all())
    maybe = Restaurant.query.filter(getattr(Restaurant, f'{attempt_2[0]}_open') <= attempt_2[1],
                                    getattr(Restaurant, f'{attempt_2[0]}_closed') >= attempt_2[1]).all()
    if maybe:
        results = results.add(maybe) if results else set(maybe)
    response = [r.name for r in results]

    return json.dumps({'success': True, 'data': response}), 200, {'ContentType': 'application/json'}


@app.route('/refresh', methods=['POST'])
def refresh():
    try:
        app_etl.etl_from_csv()
    except:
        return json.dumps({'success': False}), 501, {'ContentType': 'application/json'}
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


# Ensure db file exists and all tables created
conn = sqlite3.connect(os.path.join(BASE_PATH, 'database.db'))
conn.commit()
conn.close()
db.create_all()
if __name__ == '__main__':
    app_etl.method()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=False)
