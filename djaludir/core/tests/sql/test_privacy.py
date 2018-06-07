from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import PRIVACY

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerPrivacyTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_privacy_select(self):

        print("\n")
        print("test privacy select statement")
        print(seperator())

        sql = PRIVACY(cid = self.cid)

        if settings.DEBUG:
            print(sql)
        else:
            print("use the --debug-mode flag to print PRIVACY SQL")

        privacy = do_sql(sql, self.debug, self.earl).fetchall()

        print(privacy)

        self.assertGreaterEqual(len(privacy), 1)

    def test_privacy_select_invalid(self):

        print("\n")
        print("test privacy select statement with invalid college ID")
        print(seperator())

        sql = PRIVACY(cid = self.cid_null)

        if settings.DEBUG:
            print(sql)
        else:
            print("use the --debug-mode flag to print PRIVACY SQL")

        privacy = do_sql(sql, self.debug, self.earl).fetchall()

        print(privacy)

        self.assertEqual(len(privacy), 0)
