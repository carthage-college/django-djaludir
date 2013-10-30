# -*- coding: utf-8 -*-
import os, sys, datetime, ldap

# env
sys.path.append('/usr/local/lib/python2.7/dist-packages/')
sys.path.append('/usr/local/lib/python2.7/')
sys.path.append('/usr/lib/python2.7/dist-packages/')
sys.path.append('/usr/lib/python2.7/')
sys.path.append('/data2/django_projects/')
sys.path.append('/data2/django_third/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djaludir.settings")

from django.conf import settings

from optparse import OptionParser

# Constants
AUTH_LDAP_PROTOCOL = "ldaps"
AUTH_LDAP_PORT = '636'
AUTH_LDAP_SERVER = 'hendrix.carthage.edu'
AUTH_LDAP_BASE_USER = "cn=webldap, o=CARTHAGE"
AUTH_LDAP_BASE_PASS = "w3Bs1t3"
AUTH_LDAP_BASE = "o=CARTHAGE"
AUTH_LDAP_SCOPE = ldap.SCOPE_SUBTREE

"""
Shell script...
"""

# set up command-line options
desc = """
Accepts as input:
    first name
    last name
    username
"""

parser = OptionParser(description=desc)
parser.add_option("-gn", "--first_name", help="Person's first name.", dest="gn")
parser.add_option("-sn", "--last_name", help="Person's last name.", dest="sn")
parser.add_option("-dn", "--user_name", help="Person's username.", dest="dn")

def main():
    """
    main method
    """

    # Authenticate the base user so we can search
    try:
        l = ldap.initialize('%s://%s:%s' % (AUTH_LDAP_PROTOCOL,AUTH_LDAP_SERVER,AUTH_LDAP_PORT))
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(AUTH_LDAP_BASE_USER,AUTH_LDAP_BASE_PASS)
    except ldap.LDAPError:
        print 'authentication fail'

    philter = "(&(objectclass=person) (cn=%s))" % username
    ret = ['dn']

    result_id = l.search(base, scope, philter, ret)

    print "result_id = %s" % str(result_id)

    result_type, result_data = l.result(result_id, 0)

    print "result_type = %s" % str(result_type)
    print "result_data = %s" % str(result_data)

    # Attempt to bind to the user's DN - we don't need an if here. simple_bind will except if it fails, never return a value
    #l.simple_bind_s(result_data[0][0],password)

######################
# shell command line
######################

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    sn = options.sn
    gn = options.gn
    dn = options.dn
    if not sn:
        print "You must provide at least the person's last name.\n"
        parser.print_help()
        exit(-1)

    sys.exit(main())
