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
        relative_org = get_relative(self.cid)
        relative_new = Relative.objects.filter(user__id=self.cid)

        relatives = []
        # compare current relatives with data from POST to determine if there
        # were any changes or not
        for r1 in relative_org:
            # still not certain why we append '1' to primary relationships in
            # RELATIVES_ORIG sql so we strip it from here for now
            ro = [r1.lastname, r1.firstname, r1.relcode[:-1]]
            for r2 in relative_new:
                rn = [r2.last_name, r2.first_name, r2.relation_code]
                print(ro, rn)
                if ro != rn:
                    relatives.append(rn)

        print("comparison")
        print(relatives)
