from django.conf import settings
from django.test import TestCase

from djaludir.core.models import Address

from djtools.utils.logging import seperator


class CoreAddressTestCase(TestCase):

    fixtures = ['user.json', 'address.json']

    def setUp(self):
        self.cid = settings.TEST_USER_COLLEGE_ID

    def test_address(self):

        print("\n")
        print("test address ORM data model")
        print(seperator())

        addresses = Address.objects.filter(user__id=self.cid)

        for address in addresses:
            print(address)

        self.assertGreaterEqual(len(addresses), 1)
