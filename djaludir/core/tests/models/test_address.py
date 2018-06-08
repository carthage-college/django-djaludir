from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from djaludir.core.models import Address, EXCLUDE_FIELDS

from djtools.utils.logging import seperator

import json


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

    def test_set_address(self):
        """
        corresponds also to set_address() in manager.utils
        """

        print("\n")
        print("test address ORM data model for get_or_create() method")
        print(seperator())

        user = User.objects.get(pk=self.cid)

        json_data = open(
            '{}/core/fixtures/address.json'.format(settings.ROOT_DIR)
        ).read()
        data = json.loads(json_data)
        for i in range (0, len(data)):
            address, created = Address.objects.get_or_create(
                user = user, aa = data[i]['fields']['aa']
            )

            for f in address._meta.get_fields():
                field = f.name
                if field not in EXCLUDE_FIELDS:
                    setattr(address, field, data[0]['fields'][field])

            address.updated_by = user
            address.save()
