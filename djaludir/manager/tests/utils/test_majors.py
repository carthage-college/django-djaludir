from django.conf import settings
from django.test import TestCase

from djaludir.manager.utils import get_majors

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerUtilsMajorsTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL

    def test_get_majors(self):

        print("\n")
        print("test get_majors()")
        print(seperator())

        majors = get_majors()

        if settings.DEBUG:
            for m in majors:
                print(m)
        else:
            print("use the --debug-mode flag to print majors")

        self.assertGreaterEqual(len(majors), 1)
