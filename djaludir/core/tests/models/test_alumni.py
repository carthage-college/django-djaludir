from django.conf import settings
from django.test import TestCase

from djaludir.core.models import Alumni

from djtools.utils.logging import seperator
from djzbar.utils.informix import get_session

from sqlalchemy import desc


class CoreAlumniTestCase(TestCase):

    def setUp(self):
        #self.earl = settings.INFORMIX_EARL
        self.earl = settings.INFORMIX_EARL_TEST_DB
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_alumni(self):

        print("\n")
        print("test alumni ORM data model")
        print(seperator())

        # create database session
        session = get_session(self.earl)

        # obtain our health insturance object
        alumni = session.query(Alumni).filter_by(id=self.cid).order_by(desc(Alumni.alum_no)).first()

        print(alumni)
        #self.assertGreaterEqual(len(alumni), 1)

        # close database session
        session.close()

'''
    def test_alumni_invalid(self):

        print("\n")
        print("test alumni ORM data model with invalid college ID")
        print(seperator())

        # create database session
        session = get_session(self.earl)

        # obtain our health insturance object
        alumni = session.query(Alumni).filter_by(id=self.cid_null).order_by(desc(Alumni.alum_no)).first()

        print(alumni.id)
        #self.assertEqual(len(alumni), 0)

        # close database session
        session.close()

'''
