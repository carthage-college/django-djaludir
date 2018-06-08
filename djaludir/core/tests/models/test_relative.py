from django.conf import settings
from django.test import TestCase

from djaludir.core.models import Relative

from djtools.utils.logging import seperator


class CoreRelativeTestCase(TestCase):

    fixtures = ['user.json', 'relative.json']

    def setUp(self):
        self.cid = settings.TEST_USER_COLLEGE_ID

    def test_relative(self):

        print("\n")
        print("test relative ORM data model")
        print(seperator())

        relatives = Relative.objects.filter(user__id=self.cid)

        for relative in relatives:
            print(relative)

        self.assertGreaterEqual(len(relatives), 1)
