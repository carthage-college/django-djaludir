# -*- coding: utf-8 -*-
import os, sys, datetime

# env
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/usr/local/lib/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djaludir.settings")

from django.conf import settings

from djzbar.utils.informix import do_sql

from optparse import OptionParser

"""
Shell script...
"""

# set up command-line options
desc = """
Accepts as input a SQL statement.
"""

parser = OptionParser(description=desc)
parser.add_option("-s", "--sql", help="SQL statement.", dest="sql")

def main():
    """
    main method
    """

    objs = do_sql(sql)

    for obj in objs:
        print obj

######################
# shell command line
######################

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    sql = options.sql

    mandatories = ['sql',]
    for m in mandatories:
        if not options.__dict__[m]:
            print "mandatory option is missing: %s\n" % m
            parser.print_help()
            exit(-1)

    sys.exit(main())
