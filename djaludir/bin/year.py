# -*- coding: utf-8 -*-
import os
import sys

# env
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/data2/django_1.11/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djaludir.settings')

from djzbar.utils.informix import do_sql

import argparse

"""
obtain the start_year and end_year for students
"""

# set up command-line options
desc = """
Accepts as input a user ID.
"""

parser = argparse.ArgumentParser(description=desc)
parser.add_argument(
    '-i', '--uid',
    help = "User ID.",
    dest = 'uid',
    required = True
)
parser.add_argument(
    '--test',
    action = 'store_true',
    help = "Dry run?",
    dest = 'test'
)


def main():
    """
    main method
    """

    sql = '''
        SELECT
            MIN(yr) AS start_year, MAX(yr) AS end_year
        FROM
            stu_acad_rec WHERE id = "{}" AND yr > 0
    '''.format(uid)

    objs = do_sql(sql)

    for obj in objs:
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
    uid = args.uid
    sys.exit(main())
