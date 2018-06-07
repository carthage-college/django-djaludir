from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import RELATIVES_ORIG, RELATIVES_TEMP
from djaludir.manager.views import get_relatives

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerRelativesTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_relatives_temp(self):

        print("\n")
        print("test relatives from temp table after update")
        print(seperator())

        sql = RELATIVES_TEMP(cid = self.cid)

        if settings.DEBUG:
            print(sql)
        else:
            print("use the --debug-mode flag to print RELATIVES_TEMP SQL")

        relatives_temp = do_sql(sql, self.debug, self.earl).fetchall()

        print(relatives_temp)

    def test_relatives_orig(self):

        print("\n")
        print("test relatives from database that were already in place")
        print(seperator())

        sql = RELATIVES_ORIG(cid = self.cid)

        if settings.DEBUG:
            print(sql)
        else:
            print("use the --debug-mode flag to print RELATIVES_ORIG SQL")

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

        sql = RELATIVES_ORIG(cid = self.cid_null)

        if settings.DEBUG:
            print(sql)
        else:
            print("use the --debug-mode flag to print RELATIVES_ORIG SQL")

        relatives_orig = do_sql(sql, self.debug, self.earl).fetchall()

        print(relatives_orig)

        self.assertEqual(len(relatives_orig), 0)
