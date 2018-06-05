from django.conf import settings
from django.test import TestCase

from djaludir.core.models import Alumni

from djtools.utils.logging import seperator


class CoreAlumniTestCase(TestCase):

    fixtures = ['alumni.json','user.json']

    def setUp(self):
        self.cid = settings.TEST_USER_COLLEGE_ID

    def test_alumni(self):

        print("\n")
        print("test alumni ORM data model, which will fail if not found")
        print(seperator())

        # obtain our health insturance object
        alumni = Alumni.objects.get(user__id=self.cid)

        print(alumni)
