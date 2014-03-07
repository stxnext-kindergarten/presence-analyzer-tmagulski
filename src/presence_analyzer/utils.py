# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import threading
from datetime import datetime, timedelta
from lxml import etree
from json import dumps
from functools import wraps
from datetime import datetime

from flask import Response

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


memcached_data = {}


def cache(ttl=600):
    """
    Cache values of callable in memory for given in seconds period of time.
    """
    def cache_with_time(function):
        """
        Formal decorator for caching, take time from outer scope
        """
        @wraps(function)
        def inner(*args, **kwargs):
            global memcached_data
            memcached_key = (function.__name__, repr(args), repr(kwargs))
            if (not memcached_key in memcached_data or
               memcached_data[memcached_key]['exp_date'] < datetime.now()):
                memcached_data[memcached_key] = {
                    'exp_date': datetime.now()+timedelta(seconds=ttl),
                    'value': function(*args, **kwargs)
                }
            return memcached_data[memcached_key]['value']

        return inner

    return cache_with_time


@cache(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            'name': name,
            'avatar': avatar,
            'times': {
                datetime.date(2013, 10, 1): {
                    'start': datetime.time(9, 0, 0),
                    'end': datetime.time(17, 30, 0),
                },
                datetime.date(2013, 10, 2): {
                    'start': datetime.time(8, 30, 0),
                    'end': datetime.time(16, 45, 0),
                }
            }
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {'times': {}})['times'][date] = {
                'start': start,
                'end': end
            }

    with open(app.config['DATA_XML'], 'r') as xmlfile:
        users_info = etree.parse(xmlfile)
        server = users_info.find('./server')
        host = server.find('./host').text
        port = server.find('./port').text
        protocol = server.find('./protocol').text
        root_url = protocol+'://'+host+':'+port
        for i in users_info.findall('./users/user'):
            user_id = int(i.attrib['id'])
            name = i.find('./name').text
            avatar = i.find('./avatar').text
            if user_id in data:
                data[user_id]['name'] = name
                data[user_id]['avatar'] = root_url+avatar
    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_times_by_weekday(items, which_time):
    """
    Groups starts of presence by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        time = items[date][which_time]
        result[date.weekday()].append(seconds_since_midnight(time))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0
