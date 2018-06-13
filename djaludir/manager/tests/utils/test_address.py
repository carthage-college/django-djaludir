from django.conf import settings
from django.test import TestCase

from djaludir.manager.utils import get_alumna
from djaludir.core.models import Address, EXCLUDE_FIELDS

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerUtilsAddressTestCase(TestCase):

    fixtures = ['core/fixtures/user.json', 'core/fixtures/address.json']

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_address_comparision(self):

        print("\n")
        print("test address comparison")
        print(seperator())

        student = get_alumna(self.cid)
        addresses = Address.objects.filter(user__id=self.cid)
        data = {}

        if (len(addresses) > 0):
            for a in addresses:

                prefix = 'home'
                if a.aa == 'WORK':
                    prefix = 'business'
                for f in Address._meta.get_fields():
                    field = f.name
                    if field not in EXCLUDE_FIELDS:
                        key = '{}_{}'.format(prefix, field)
                        val = getattr(a, field)
                        if student[key] != val:
                            data[key] = val
                            orig_key = 'original_{}'.format(key)
                            data[orig_key] = student[key]
                            data[prefix] = True
        print(data)
