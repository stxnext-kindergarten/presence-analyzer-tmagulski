# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, render_template, url_for, abort
from jinja2 import TemplateNotFound

from presence_analyzer.main import app
from presence_analyzer import utils

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


@app.route('/')
@app.route('/<view>')
def ui_view(view=None):
    """
    View responsible for generating UI for all tempalates
    """
    titles = {'presence_weekday': 'Presence by weekday',
              'mean_time_weekday': 'Presence mean time by weekday',
              'presence_start_end': 'Presence start-end weekday'}
    if view is None:
        return redirect(url_for('ui_view', view='presence_weekday'))
    else:
        try:
            return render_template(view + '.html', title=titles[view])
        except KeyError, TemplateNotFound:
            abort(404)


@app.route('/api/v1/users', methods=['GET'])
@utils.jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = utils.get_data()
    response = []
    for i in data.keys():
        if 'name' in data[i]:
            response.append({'user_id': i, 'name': data[i]['name']})
        else:
            response.append({'user_id': i, 'name': 'User {0}'.format(str(i))})
    return response


@app.route('/api/v1/mean_time_weekday/', methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def mean_time_weekday_view(user_id=None):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_by_weekday(data[user_id]['times'])
    result = [(calendar.day_abbr[weekday], utils.mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/', methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = utils.group_by_weekday(data[user_id]['times'])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/', methods=['GET'])
@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@utils.jsonify
def presence_start_end_view(user_id=None):
    """
    Return mean times of start and and of work for given user.
    """
    data = utils.get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    starts = utils.group_times_by_weekday(data[user_id]['times'], 'start')
    ends = utils.group_times_by_weekday(data[user_id]['times'], 'end')
    result = [(calendar.day_abbr[weekday],
               utils.mean(starts[weekday]),
               utils.mean(ends[weekday]))
              for weekday in starts if len(starts[weekday]) > 0]
    return result
