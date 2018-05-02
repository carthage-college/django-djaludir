from django.conf import settings
from django.test import TestCase
from django_webtest import WebTest
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from djaludir.core.sql import ALUMNA, RELATIVES_ORIG, RELATIVES_TEMP
from djaludir.manager.views import get_relatives

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


import logging
logger = logging.getLogger(__name__)


class CoreSQLTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.student_number = settings.TEST_STUDENT_NUMBER
        self.student_number_null = 666
        self.earl = settings.INFORMIX_EARL

    def test_relatives_temp(self):

        print("\n")
        print("test relatives from temp table after update")
        print(seperator())

        sql = RELATIVES_TEMP(student_number = self.student_number)
        print(sql)

        relatives_temp = do_sql(sql, self.debug, self.earl).fetchall()

        print(relatives_temp)

    def test_relatives_orig(self):

        print("\n")
        print("test relatives from database that were already in place")
        print(seperator())

        sql = RELATIVES_ORIG(student_number = self.student_number)
        print(sql)

        relatives_orig = do_sql(sql, self.debug, self.earl).fetchall()

        print(relatives_orig)

        self.assertGreaterEqual(len(relatives_orig), 1)

    def test_relatives_orig_invalid(self):

        print("\n")
        print(
            """
            test relatives from database that were already in place
            with invalid ID
            """
        )
        print(seperator())

        sql = RELATIVES_ORIG(student_number = self.student_number_null)
        print(sql)

        relatives_orig = do_sql(sql, self.debug, self.earl).fetchall()

        print(relatives_orig)

    def test_relatives_comparision(self):

        relatives_orig = get_relatives(self.student_number)
        relatives_sql = RELATIVES_TEMP(student_number = self.student_number)
        relatives_new = do_sql(relatives_sql, self.debug, self.earl).fetchall()
        relatives = []
        for r1 in relatives_orig:
            ro = list(r1)
            del ro[3]
            for r2 in relatives_new:
                rn = list(r2)
                if ro != rn:
                    relatives.append(rn)

        print("comparison")
        print(relatives)
