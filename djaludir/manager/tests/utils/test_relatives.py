from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import RELATIVES_TEMP
from djaludir.manager.views import get_relatives

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerUtilsRelativesTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.cid = settings.TEST_COLLEGE_ID
        self.cid_null = 666
        self.earl = settings.INFORMIX_EARL

    def test_relatives_comparision(self):

        relatives_orig = get_relatives(self.cid)
        relatives_sql = RELATIVES_TEMP(cid = self.cid)
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
