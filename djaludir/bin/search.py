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

from django.conf import settings

from djaludir.registration import SEARCH, SEARCH_ORDER_BY, SEARCH_GROUP_BY
from djzbar.utils.informix import do_sql
from djzbar.settings import INFORMIX_EARL_PROD as EARL

import argparse

# set up command-line options
desc = """
Accepts as input first, last name, and DOB
"""

parser = argparse.ArgumentParser(description=desc)

parser.add_argument('-f', '--first', help="First name", dest="first")
parser.add_argument('-l', '--last', help="Last name", dest="last")
parser.add_argument('-d', '--dob', help="Date of Birth", dest="dob")
parser.add_argument('-e', '--email', help="email", dest="email")
parser.add_argument('-i', '--id', help="college ID", dest="cid")
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test'
)


def main():
    """
    main method
    """

    # if we have a college id we are good to go
    if cid:
        where = ' id_rec.id = "{}"'.format(cid)
    else:
        where = '''
            lower(id_rec.firstname) like "%%{}%%" OR
            lower(aname_rec.line1) like "%%{}%%"
        '''.format(
            first.lower(), first.lower()
        )
        where += ' AND lower(id_rec.lastname) = "{}"'.format(last.lower())
        if dob:
            where+= ' AND'
            where+= ' profile_rec.birth_date = "{}"'.format(dob)
        if email:
            where+= ' AND'
            where+= ' email_rec.line1 = "{}"'.format(email)

    sql = SEARCH+ where
    sql += SEARCH_GROUP_BY
    sql += SEARCH_ORDER_BY
    if test:
        print sql
    objs = do_sql(sql, earl=EARL, key='debug')
    if test:
        print objs
    objects = objs.fetchall()
    if test:
        print len(objects)
        print objects[0].id
    for obj in objects:
        print "obj dict id = {}".format(obj['id'])
        print obj


######################
# shell command line
######################

if __name__ == '__main__':

    args = parser.parse_args()
    test = args.test

    if test:
        print args

    # vars
    cid = args.cid
    first = args.first
    last = args.last
    dob = args.dob
    email = args.email
    # if we have a college id we are good to go
    if not cid:
        mandatories = ['first','last','dob']
        for m in mandatories:
            if not args.__dict__[m]:
                print "mandatory option is missing: {}\n".format(m)
                parser.print_help()
                exit(-1)

    sys.exit(main())
