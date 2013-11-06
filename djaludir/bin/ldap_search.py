# -*- coding: utf-8 -*-
"""
Notes:

password is MD5 hash?
http://www.openldap.org/lists/openldap-software/200011/msg00268.html

userpassword: {MD5}X03MO1qnZdYdgyfeuILPmQ==

https://groups.google.com/forum/#!topic/novell.support.edirectory.windows/Y7PaE5zC47c

userpassword is a write-only attribute. You can't read it.

add example:
http://www.grotan.com/ldap/python-ldap-samples.html#add
"""

from optparse import OptionParser

import os, sys, datetime, ldap

# env
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/usr/local/lib/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djaludir.settings")

# now we can import settings
from django.conf import settings

# set up command-line options
desc = """
Accepts as input:
    first name
    last name
    username
"""

parser = OptionParser(description=desc)
parser.add_option("-g", "--first_name", help="Person's first name.", dest="g")
parser.add_option("-s", "--last_name", help="Person's last name.", dest="s")
parser.add_option("-d", "--user_name", help="Person's username.", dest="d")

def main():
    """
    main method
    """

    # Authenticate the base user so we can search
    try:
        l = ldap.initialize('%s://%s:%s' % (settings.LDAP_PROTOCOL,settings.LDAP_SERVER,settings.LDAP_PORT))
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(settings.LDAP_USER,settings.LDAP_PASS)
    except ldap.LDAPError:
        print 'authentication fail'

    #username = "skirk"
    #username = "eyoung"
    #philter = "(&(objectclass=person) (cn=%s))" % username
    philter = "(&(objectclass=carthageUser) (cn=%s))" % d
    #ret = ['userpassword']
    ret = ['cn','givenName','sn','mail','carthageDob','carthageStaffStatus','carthageFacultyStatus','carthageNameID','carthageSSN','userPassword']

    result_id = l.search(settings.LDAP_BASE, ldap.SCOPE_SUBTREE , philter, ret)

    print "result_id = %s" % str(result_id)

    result_type, result_data = l.result(result_id, 0)

    print "result_type = %s" % str(result_type)
    #print "result_data = %s" % str(result_data)
    print "result_data = %s" % str(result_data[0][1])

######################
# shell command line
######################

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    g = options.g
    s = options.s
    d = options.d
    if not s or not d:
        print "You must provide at least the person's last name or username.\n"
        parser.print_help()
        exit(-1)

    sys.exit(main())
