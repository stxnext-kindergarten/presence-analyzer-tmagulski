# -*- coding: utf-8 -*-
"""Script that download fresh xml with users' names and urls for avatars"""

import urllib2

from script import make_app

import logging
log = logging.getLogger(__name__)  # pylint: disable-msg=C0103


def run():
    app = make_app()
    with open(app.config['DATA_XML'], 'w') as xml_file:
        try:
            new_xml = urllib2.urlopen(app.config['REMOTE_XML']).read()
        except URLError:
            log.debug('Problem with fetching xml from remote location.')
        except KeyError:
            log.debug('REMOTE_XML not configured in configuration of app.')
        else:
            xml_file.write(new_xml)
