from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import ALUMNA, ALUMNA_TEMP

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerAlumnaTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_alumna(self):

        print("\n")
        print("test alumna select statement")
        print(seperator())

        sql = ALUMNA(cid = self.cid, deceased = '')
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertGreaterEqual(len(alumna), 1)

    def test_alumna_invalid(self):

        print("\n")
        print("test alumna select statement with invalid college ID")
        print(seperator())

        sql = ALUMNA(cid = self.cid_null, deceased = '')
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertEqual(len(alumna), 0)

    def test_alumna_temp(self):

        print("\n")
        print("test alumna temp table select statement")
        print(seperator())

        sql = ALUMNA_TEMP(cid = self.cid)
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertGreaterEqual(len(alumna), 1)

    def test_alumna_temp_invalid(self):

        print("\n")
        print("test alumna select statement with invalid college ID")
        print(seperator())

        sql = ALUMNA_TEMP(cid = self.cid_null)
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertEqual(len(alumna), 0)
