# -*- coding: utf-8 -*-
import os, sys
# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.11/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djaludir.settings')

# required if using django models
import django
django.setup()

from django.conf import settings
from django.contrib.auth.models import User

from djzbar.utils.informix import do_sql
from djzbar.settings import INFORMIX_EARL_PROD_DRDA as INFORMIX_EARL

import argparse

'''
Find deceased alumni
'''

EARL = settings.INFORMIX_EARL

# set up command-line options
desc = """
    Find deceased alumni
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)

def main():
    '''
    main function
    '''

    if test:
        print 'test run'

    users = User.objects.all()

    uid = []
    for u in users:
        uid.append(int(u.id))
    if test:
        print uid

    sql = '''
        select * from profile_rec where id in {} and decsd_date is not null
        order by id
    '''.format(tuple(uid))

    if test:
        print sql

    sqlresult = do_sql(sql, earl=EARL)
    if sqlresult:
        for s in sqlresult:
            print s.id, s.decsd_date


######################
# shell command line
######################

if __name__ == '__main__':
    args = parser.parse_args()
    test = args.test

    if test:
        print args

    sys.exit(main())

