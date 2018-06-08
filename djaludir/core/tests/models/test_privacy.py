from django.conf import settings
from django.test import TestCase

from djaludir.core.models import Privacy

from djtools.utils.logging import seperator


class CorePrivacyTestCase(TestCase):

    fixtures = ['user.json', 'privacy.json']

    def setUp(self):
        self.cid = settings.TEST_USER_COLLEGE_ID

    def test_privacy(self):

        print("\n")
        print("test privacy ORM data model")
        print(seperator())

        privacies = Privacy.objects.filter(user__id=self.cid)
        print("len = {}".format(len(privacies)))
        for privacy in privacies:
            print(privacy)

        self.assertGreaterEqual(len(privacies), 1)
