from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import ACTIVITIES_TEMP
from djaludir.manager.utils import get_activities

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerUtilsActivitiesTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_activities_comparision(self):

        print("\n")
        print("test activities comparison")
        print(seperator())

        activities = get_activities(self.cid, False)
        athletics = get_activities(self.cid, True)

        activities_temp = do_sql(
            ACTIVITIES_TEMP(cid = self.cid), self.earl
        ).fetchall()

        activities_orig = []

        for a in activities:
            activities_orig.append(a)

        for a in athletics:
            activities_orig.append(a)

        print("activities_orig")
        print(activities_orig)

        activities_diff = []
        for temp in activities_temp:
            if temp not in activities_orig:
                activities_diff.append(temp)

        print("activities_diff")
        print(activities_diff)
