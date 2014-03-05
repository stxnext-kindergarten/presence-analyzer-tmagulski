# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, render_template, url_for

from presence_analyzer.main import app
from presence_analyzer import utils

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('presence_weekday_ui_view'))


@app.route('/presence_weekday')
def presence_weekday_ui_view():
    """
    Rendering presence weekday view for web UI.
    """
    return render_template('presence_weekday.html',
                           title='Presence by weekday')


@app.route('/mean_time_weekday')
def mean_time_weekday_ui_view():
    """
    Rendering mean time weekday view for web UI.
    """
    return render_template('mean_time_weekday.html',
                           title='Presence mean time by weekday')


@app.route('/presence_start_end')
def presence_start_end_ui_view():
    """
    Rendering presence start end view for web UI.
    """
    return render_template('presence_start_end.html',
                           title='Presence start-end weekday')


@app.route('/api/v1/users', methods=['GET'])
@utils.jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = utils.get_data()
    return [{'user_id': i, 'name': 'User {0}'.format(str(i))}
            for i in data.keys()]


@app.route('/api/v1/mean_time_weekday/',
           methods=['GET'],
           defaults={'user_id': None})
@app.route('/api/v1/mean_time_weekday/<user_id>', methods=['GET'])
@utils.jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    user_id = int(user_id)
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], utils.mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/',
           methods=['GET'],
           defaults={'user_id': None})
@app.route('/api/v1/presence_weekday/<user_id>', methods=['GET'])
@utils.jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    user_id = int(user_id)
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/',
           methods=['GET'],
           defaults={'user_id': None})
@app.route('/api/v1/presence_start_end/<user_id>', methods=['GET'])
@utils.jsonify
def presence_start_end_view(user_id):
    """
    Return mean times of start and and of work for given user.
    """
    user_id = int(user_id)
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    starts = utils.group_times_by_weekday(data[user_id], 'start')
    ends = utils.group_times_by_weekday(data[user_id], 'end')
    result = [(calendar.day_abbr[weekday],
               utils.mean(starts[weekday]),
               utils.mean(ends[weekday]))
              for weekday in starts if len(starts[weekday]) > 0]
    return result
