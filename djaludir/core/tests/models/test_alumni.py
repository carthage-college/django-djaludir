from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from djaludir.core.models import Alumna, EXCLUDE_FIELDS

from djtools.utils.logging import seperator

import json


class CoreAlumnaTestCase(TestCase):

    fixtures = ['alumni.json','user.json']

    def setUp(self):
        self.cid = settings.TEST_USER_COLLEGE_ID

    def test_get_alumna(self):

        print("\n")
        print("test alumna ORM data model, which will fail if not found")
        print(seperator())

        # obtain our health insturance object
        alumna = Alumna.objects.get(user__id=self.cid)

        print(alumna)

    def test_set_alumna(self):
        """
        corresponds also to the set_alumna() in manager.utils
        """

        print("\n")
        print("test alumna ORM data model for get_or_create() method")
        print(seperator())

        user = User.objects.get(pk=self.cid)

        alumna, created = Alumna.objects.get_or_create(user = user)

        json_data = open(
            '{}/core/fixtures/alumni.json'.format(settings.ROOT_DIR)
        ).read()
        data = json.loads(json_data)
        for f in alumna._meta.get_fields():
            field = f.name
            if field not in EXCLUDE_FIELDS:
                setattr(alumna, field, data[0]['fields'][field])
        alumna.updated_by=(user)
        alumna.save()
