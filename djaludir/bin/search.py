# -*- coding: utf-8 -*-
import os, sys

# env
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/usr/local/lib/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djaludir.settings")

from django.conf import settings

from djaludir.registration import SEARCH, SEARCH_ORDER_BY, SEARCH_GROUP_BY
from djzbar.utils.informix import do_sql

from optparse import OptionParser

# set up command-line options
desc = """
Accepts as input first, last name, and DOB
"""

parser = OptionParser(description=desc)
parser.add_option("-f", "--first", help="First name", dest="first")
parser.add_option("-l", "--last", help="Last name", dest="last")
parser.add_option("-d", "--dob", help="Date of Birth", dest="dob")
parser.add_option("-e", "--email", help="email", dest="email")
parser.add_option("-i", "--id", help="college ID", dest="cid")

def main():
    """
    main method
    """

    # if we have a college id we are good to go
    if cid:
        where = ' id_rec.id = "%s"' % cid
    else:
        where = (' ( lower(id_rec.firstname) like "%%%s%%" OR'
                 ' lower(aname_rec.line1) like "%%%s%%" )'
        % (first.lower(),first.lower()))
        where += (' AND lower(id_rec.lastname) = "%s"' % (last.lower()))
        if dob:
            where+= ' AND'
            #where+= ' profile_rec.birth_date = "%s"' % dob.strftime("%m/%d/%Y")
            where+= ' profile_rec.birth_date = "%s"' % dob
        if email:
            where+= ' AND'
            where+= ' email_rec.line1 = "%s"' % email

    sql = SEARCH+ where
    sql += SEARCH_GROUP_BY
    sql += SEARCH_ORDER_BY

    print sql
    objs = do_sql(sql, key="debug")
    for obj in objs:
        print obj

######################
# shell command line
######################

if __name__ == "__main__":
    # input from command line
    (options, args) = parser.parse_args()
    # vars
    cid = options.cid
    first = options.first
    last = options.last
    dob = options.dob
    email = options.email
    # if we have a college id we are good to go
    if not cid:
        mandatories = ['first','last','dob']
        for m in mandatories:
            if not options.__dict__[m]:
                print "mandatory option is missing: %s\n" % m
                parser.print_help()
                exit(-1)

    sys.exit(main())
