# -*- coding: utf-8 -*-
"""Script that download fresh xml with users' names and urls for avatars"""

import urllib2

from script import make_app

def run():
    app = make_app()
    with open(app.config['DATA_XML'], 'w') as xml_file:
        try:
            new_xml = urllib2.urlopen(app.config['REMOTE_XML']).read()
        except:
            pass
        xml_file.write(new_xml)
