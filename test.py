import unittest

import app


class TestETL(unittest.TestCase):

    def test_standardize_ts(self):
        etl = app.ETL(None)
        result = {
            'monday_open': 1100, 'monday_closed': 2230,
            'tuesday_open': 1100, 'tuesday_closed': 2230,
            'wednesday_open': 1100, 'wednesday_closed': 2230,
            'thursday_open': 1100, 'thursday_closed': 2230,
            'friday_open': 1100, 'friday_closed': 2230,
            'sunday_open': 1100, 'sunday_closed': 2230
        }
        self.assertEqual(etl.standardize_ts(ts_str='Mon-Fri, Sun 11 am - 10:30 pm'), result)

        result = {
            'monday_open': 1030, 'monday_closed': 2300,
            'tuesday_open': 1030, 'tuesday_closed': 2300,
            'wednesday_open': 1030, 'wednesday_closed': 2300,
            'thursday_open': 1030, 'thursday_closed': 2300,
            'friday_open': 1030, 'friday_closed': 2300,
            'sunday_open': 1030, 'sunday_closed': 2300
        }
        self.assertEqual(etl.standardize_ts(ts_str='Mon-Fri, Sun 10:30 am - 11 pm'), result)

        result = {
            'monday_open': 1100, 'monday_closed': 2230,
            'tuesday_open': 1100, 'tuesday_closed': 2230,
            'wednesday_open': 1100, 'wednesday_closed': 2230,
            'friday_open': 1100, 'friday_closed': 2230,
            'sunday_open': 1100, 'sunday_closed': 2230
        }
        self.assertEqual(etl.standardize_ts(ts_str='Mon-Wed, Fri, Sun 11 am - 10:30 pm'), result)

        result = {
            'saturday_open': 1600, 'saturday_closed': 2630,
        }
        self.assertEqual(etl.standardize_ts(ts_str='Sat 4 pm - 2:30 am'), result)

    def test_interpret_ts(self):
        from datetime import datetime
        self.assertEqual(app.interpret_ts('2009/06/06 13:30:10'),
                         datetime.strptime('2009/06/06 13:30:10', '%Y/%m/%d %H:%M:%S'))










