# -*- coding: utf-8 -*-
"""
Add a user to LDAP store
"""

from optparse import OptionParser

import os, sys, ldap
import ldap.modlist as modlist

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
Accepts as input and all are required:
    first name
    last name
    username
    date of birth
    group (faculty,staff,student,alumni)
    college ID
    email
    password enclosed in quotes
"""

parser = OptionParser(description=desc)
parser.add_option("-f", "--first_name", help="Person's first name.", dest="givenName")
parser.add_option("-l", "--last_name", help="Person's last name.", dest="sn")
parser.add_option("-d", "--user_name", help="Person's username.", dest="cn")
parser.add_option("-b", "--dob", help="Date of birth.", dest="carthageDob")
parser.add_option("-g", "--group", help="Person's group.", dest="group")
parser.add_option("-i", "--id", help="Person's college ID.", dest="carthageNameID")
parser.add_option("-m", "--email", help="Person's email.", dest="mail")
parser.add_option("-p", "--password", help="Person's password enclosed in quotes.", dest="userPassword")

def main():
    """
    main method
    """

    # Authenticate the base user so we can search
    if settings.DEBUG:
        l = ldap.initialize("%s://%s:%s" % (settings.LDAP_PROTOCOL, settings.LDAP_SERVER, settings.LDAP_PORT))
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(settings.LDAP_USER,settings.LDAP_PASS)
    #except ldap.LDAPError:
    else:
        print 'authentication fail'
        exit(-1)

    # If there is only one value in the attribute value list,
    # the value can be just a string – it need not be a list.
    # Example: ('ou', 'user') is an acceptable alternative to
    # ('ou', ['user']).
    #    "objectclass":["User","carthageUser"],

    person = {
        "objectclass":["User","carthageUser"],
        "givenName":givenName,"sn":sn,"cn":cn,"loginDisabled":"false",
        "carthageDob":carthageDob,"carthageNameID":carthageNameID,
        "mail":mail,"userPassword":userPassword
    }

    if group.lower()=="faculty":
        person["carthageFacultyStatus"] = "A"
    elif group.lower()=="staff":
        person["carthageStaffStatus"] = "A"
    elif group.lower()=="student":
        person["carthageStudentStatus"] = "A"
    elif group.lower()=="alumni":
        person["carthageFormerStudentStatus"] = "A"
    else:
        person["carthageOtherStatus"] = "A"

    print cn
    print person
    user = modlist.addModlist(person)
    print user

    dn = 'cn=%s,%s' % (cn,settings.LDAP_BASE)
    l.add_s(dn, user)

######################
# shell command line
######################

if __name__ == "__main__":
    (options, args) = parser.parse_args()

    missing_options = []
    for option in parser.option_list:
        if option.dest:
            if eval('options.' + option.dest) == None:
                missing_options.extend(option._long_opts)

    if len(missing_options) > 0:
        print 'Missing parameters that are required:\n%s\n' % str(missing_options)
        parser.print_help()
        exit(-1)
    else:
        for option in parser.option_list:
            if option.dest:
                locals()['%s' % str(option.dest)] = eval('options.' + option.dest)
    sys.exit(main())
