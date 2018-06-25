from django.conf import settings
from django.test import TestCase

from djaludir.manager.utils import get_relative
from djaludir.core.models import Relative

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerUtilsRelativeTestCase(TestCase):

    fixtures = ['core/fixtures/user.json', 'core/fixtures/relative.json']

    def setUp(self):
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_relative_comparision(self):

        # Get information about the alum's relatives
        relative_orig = get_relative(self.cid)
        relative_temp = Relative.objects.filter(user__id=self.cid)

        orig = set()
        temp = set()
        for r in relative_orig:
            # still not certain why we append '1' to primary relationships in
            # RELATIVES_ORIG sql so we strip it from here for now
            orig.add((r.lastname, r.firstname, r.relcode[:-1]))
        for r in relative_temp:
            temp.add((r.last_name, r.first_name, r.relation_code))

        relatives = orig.symmetric_difference(temp)
        print("comparison")
        print(relatives)
