from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import HOMEADDRESS_TEMP, WORKADDRESS_TEMP

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerAddressTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_home_address_temp(self):

        print("\n")
        print("test home address select statement from temp table")
        print(seperator())

        sql = HOMEADDRESS_TEMP(cid = self.cid)
        print(sql)

        homeaddress = do_sql(sql, self.debug, self.earl).fetchall()

        print(homeaddress)

        self.assertGreaterEqual(len(homeaddress), 1)

    def test_home_address_invalid(self):

        print("\n")
        print(
            """
            test home address select statement from temp table
            with invalid college ID
            """
        )
        print(seperator())

        sql = HOMEADDRESS_TEMP(cid = self.cid_null)
        print(sql)

        homeaddress = do_sql(sql, self.debug, self.earl).fetchall()

        print(homeaddress)

        self.assertEqual(len(homeaddress), 0)

    def test_work_address_temp(self):

        print("\n")
        print("test work address select statement from temp table")
        print(seperator())

        sql = WORKADDRESS_TEMP(cid = self.cid)
        print(sql)

        workaddress = do_sql(sql, self.debug, self.earl).fetchall()

        print(workaddress)

        self.assertGreaterEqual(len(workaddress), 1)

    def test_work_address_invalid(self):

        print("\n")
        print(
            """
            test work address select statement from temp table
            with invalid college ID
            """
        )
        print(seperator())

        sql = WORKADDRESS_TEMP(cid = self.cid_null)
        print(sql)

        workaddress = do_sql(sql, self.debug, self.earl).fetchall()

        print(workaddress)

        self.assertEqual(len(workaddress), 0)

