from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from djaludir.core.models import Relative

from djtools.utils.logging import seperator

import json


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

    def test_set_relative(self):
        """
        corresponds also to set_relative() in manager.utils
        """

        print("\n")
        print("test relative ORM data model for get_or_create() method")
        print(seperator())

        user = User.objects.get(pk=self.cid)

        json_data = open(
            '{}/core/fixtures/relative.json'.format(settings.ROOT_DIR)
        ).read()
        data = json.loads(json_data)
        for i in range (0, len(data)):
            relative, created = Relative.objects.get_or_create(
                user = user,
                relation_code = data[i]['fields']['relation_code'],
                first_name = data[i]['fields']['first_name'],
                last_name = data[i]['fields']['last_name']
            )
            relative.updated_by = user
            relative.primary = data[i]['fields']['primary']
            relative.save()
