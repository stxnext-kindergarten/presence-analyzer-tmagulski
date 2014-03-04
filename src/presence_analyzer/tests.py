# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import calendar
import numbers
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)


# pylint: disable=E1103
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {u'user_id': 10, u'name': u'User 10'})

    def test_api_mean_time(self):
        """
        Test mean times of user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 7)
        for weekday in data:
            self.assertEqual(len(weekday), 2)
            self.assertTrue(weekday[0] in calendar.day_abbr)
            self.assertIsInstance(weekday[1], numbers.Number)
        resp = self.client.get('/api/v1/mean_time_weekday/100')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)
        self.assertListEqual(data, [])

    def test_api_presence(self):
        """
        Test presence of user.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 8)
        self.assertListEqual(data[0], ['Weekday', 'Presence (s)'])
        for weekday in data[1:]:
            self.assertEqual(len(weekday), 2)
            self.assertTrue(weekday[0] in calendar.day_abbr)
            self.assertIsInstance(weekday[1], numbers.Number)
        resp = self.client.get('/api/v1/presence_weekday/100')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)
        self.assertEqual(data, [])

    def test_api_start_end(self):
        """
        Test start and end of user.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertLess(len(data), 8)
        for weekday in data:
            self.assertEqual(len(weekday), 3)
            self.assertTrue(weekday[0] in calendar.day_abbr)
            self.assertIsInstance(weekday[1], numbers.Number)
            self.assertIsInstance(weekday[2], numbers.Number)
            self.assertLess(weekday[1], weekday[2])
        resp = self.client.get('/api/v1/presence_start_end/100')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 0)
        self.assertListEqual(data, [])


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'],
                         datetime.time(9, 39, 5))

    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight.
        """
        sample_time = datetime.time(0, 0, 0)
        data = utils.seconds_since_midnight(sample_time)
        self.assertEqual(data, 0)
        sample_time = datetime.time(0, 0, 1)
        data = utils.seconds_since_midnight(sample_time)
        self.assertEqual(data, 1)
        sample_time = datetime.time(0, 1, 0)
        data = utils.seconds_since_midnight(sample_time)
        self.assertEqual(data, 60)
        sample_time = datetime.time(1, 0, 0)
        data = utils.seconds_since_midnight(sample_time)
        self.assertEqual(data, 3600)
        sample_time = datetime.time(23, 59, 59)
        data = utils.seconds_since_midnight(sample_time)
        self.assertEqual(data, 86399)


def suite():
    """
    Default test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return suite


if __name__ == '__main__':
    unittest.main()
