from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from djaludir.core.models import Activity

from djtools.utils.logging import seperator

import json


class CoreActivityTestCase(TestCase):

    fixtures = ['user.json', 'activity.json']

    def setUp(self):
        self.cid = settings.TEST_USER_COLLEGE_ID

    def test_activity(self):

        print("\n")
        print("test activity ORM data model")
        print(seperator())

        activities = Activity.objects.filter(user__id=self.cid)

        for activity in activities:
            print(activity)

        self.assertGreaterEqual(len(activities), 1)

    def test_set_relative(self):
        """
        corresponds also to set_relative() in manager.utils
        """

        print("\n")
        print("test relative ORM data model for get_or_create() method")
        print(seperator())

        user = User.objects.get(pk=self.cid)

        json_data = open(
            '{}/core/fixtures/activity.json'.format(settings.ROOT_DIR)
        ).read()
        data = json.loads(json_data)
        for i in range (0, len(data)):
            activity, created = Activity.objects.get_or_create(
                user = user, text = data[i]['fields']['text'],
                code = data[i]['fields']['code']
            )
            activity.updated_by = user
            activity.save()
