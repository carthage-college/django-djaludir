# -*- coding: utf-8 -*-
from django.conf import settings

import ldap
import ldap.modlist as modlist

class LDAPManager:

    def __init__(self):
        # Authenticate the base user so we can search
        try:
            self.l = ldap.initialize('%s://%s:%s' % (
                    settings.LDAP_PROTOCOL,settings.LDAP_SERVER,
                    settings.LDAP_PORT
                )
            )
            self.l.protocol_version = ldap.VERSION3
            self.l.simple_bind_s(settings.LDAP_USER,settings.LDAP_PASS)
        except ldap.LDAPError, e:
            raise Exception(e)

    def create(self, person):
        """
        Creates a new LDAP user.
        Takes as argument a dictionary with the following key/value pairs:

        givenName       [first name]
        sn              [last name]
        cn              [username]
        carthageDob     [date of birth]
        group           [faculty,staff,student,alumni,other]
        carthageNameID  [college ID]
        mail            [email]
        userPassword    [password]
        """

        group = person["group"]

        if group.lower()=="faculty":
            person["carthageFacultyStatus"] = "A"
        elif group.lower()=="staff":
            person["carthageStaffStatus"] = "A"
        elif group.lower()=="student":
            person["carthageStudentStatus"] = "A"
        elif group.lower()=="alumni":
            person["carthageAlumniStatus"] = "A"
        else:
            person["carthageOtherStatus"] = "A"

        user = modlist.addModlist(person)

        dn = 'cn=%s,ou=USERS,o=CARTHAGE' % (cn)
        self.l.add_s(dn, user,)

    def delete(self, person):
        """
        Deletes an LDAP user.
        Takes as argument a dictionary with the following key/value pairs:

        cn              [username]
        group           [faculty,staff,student,alumni,other]
        """

        deleteDN = "cn=%s,ou=%s,o=CARTHAGE" % (person["username"],person["group"])
        try:
            # we can safely ignore the results returned, since an exception
            # will be raised if the delete doesn't work.
            self.l.delete_s(deleteDN)
        except ldap.LDAPError, e:
            pass

    def search(self, username):
        """
        Searches for an LDAP user.
        Takes as argument a username (cn).
        Returns a dictionary with the following key/value pairs:

        givenName               [first name]
        sn                      [last name]
        cn                      [username]
        carthageDob             [date of birth]
        carthageNameID          [college ID]
        carthageStaffStatus     [staff?]
        carthageOtherStatus     [alumni?]
        carthageFacultyStatus   [faculty?]
        carthageStudentStatus   [student?]
        mail                    [email]
        userPassword            [password]
        """

        philter = "(&(objectclass=carthageUser) (cn=%s))" % username
        ret = [
            'cn','givenName','sn','mail','carthageDob','carthageNameID',
            'carthageSSN','carthageStaffStatus','carthageFacultyStatus',
            'carthageStudentStatus'
        ]

        result_id = self.l.search(
            settings.LDAP_BASE,settings.LDAP_SCOPE,philter,ret
        )
        result_type, result_data = self.l.result(result_id, 0)

        try:
            r = result_data[0][1]
        except:
            r = None
        return r
