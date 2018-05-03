from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import ACTIVITIES, ACTIVITIES_TEMP

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerActivitiesTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.cid = settings.TEST_COLLEGE_ID
        self.cid_invalid = 666
        self.earl = settings.INFORMIX_EARL

    def test_activities(self):

        print("\n")
        print("test activities select statement")
        print(seperator())

        # organization, club, etc.
        sport = False
        fieldname = 'activity' if not is_sports else 'sport'
        comparison = 'NOT' if not is_sports else ''

        sql = ACTIVITIES(
            cid = self.cid, fieldname = fieldname, comparison = comparision
        )

        print(sql)

        activities = do_sql(sql, self.debug, self.earl).fetchall()

        print(activities)

        self.assertGreaterEqual(len(activities), 1)

    def test_activities_invalid(self):

        print("\n")
        print("test activities select statement with invalid college ID")
        print(seperator())

        # organization, club, etc.
        sport = False
        fieldname = 'activity' if not is_sports else 'sport'
        comparison = 'NOT' if not is_sports else ''

        sql = ACTIVITIES(
            cid = self.cid_invalid, fieldname = fieldname, comparison = comparision
        )

        print(sql)

        activities = do_sql(sql, self.debug, self.earl).fetchall()

        print(activities)

        self.assertEqual(len(activities), 0)

    def test_activities_temp(self):

        print("\n")
        print("test activities select statement from temp table")
        print(seperator())


        sql = ACTIVITIES(cid = self.cid)

        print(sql)

        activities = do_sql(sql, self.debug, self.earl).fetchall()

        print(activities)

        self.assertEqual(len(activities), 0)

