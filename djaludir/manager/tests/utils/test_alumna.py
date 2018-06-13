from django.conf import settings
from django.test import TestCase

from djaludir.manager.utils import get_alumna, set_alumna

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerUtilsRelativesTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_alumna(self):

        print("\n")
        print("test get_alumna() with valid college ID")
        print(seperator())

        alumna = get_alumna(self.cid)

        self.assertGreaterEqual(len(alumna), 1)

    def test_alumna_invalid(self):

        print("\n")
        print("test get_alumna() with invalid college ID")
        print(seperator())

        alumna = get_alumna(self.cid_null)

        self.assertIsNone(alumna)
