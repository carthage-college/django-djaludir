# -*- coding: utf-8 -*-
from django.conf import settings

import ldap
import ldap.modlist as modlist

class LDAPManager(object):

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

        objectclass     ["User","carthageUser"]
        givenName       [first name]
        sn              [last name]
        carthageDob     [date of birth]
        carthageNameID  [college ID]
        cn              [we use email for username]
        mail            [email]
        userPassword    [password]
        """
        person["carthageFacultyStatus"] = ""
        person["carthageStaffStatus"] = ""
        person["carthageStudentStatus"] = ""
        person["carthageFormerStudentStatus"] = "A"
        person["carthageOtherStatus"] = ""

        user = modlist.addModlist(person)

        dn = 'cn=%s,ou=USERS,o=CARTHAGE' % (cn)
        self.l.add_s(dn, user,)

    def update(self, person):
        """
        Updates an LDAP user.
        """
        return False

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

    def search(self, val, field="carthageNameID"):
        """
        Searches for an LDAP user.
        Takes as argument a value and a valid unique field from
        the schema (i.e. carthageNameID, cn, mail).
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
        """

        valid = ["cn","carthageNameID","mail"]
        if field not in valid:
            return None
        philter = "(&(objectclass=carthageUser) (%s=%s))" % (field,val)
        ret = [
            'cn','givenName','sn','mail','carthageDob','carthageNameID',
            'carthageSSN','carthageStaffStatus','carthageFacultyStatus',
            'carthageStudentStatus'
        ]

        result_id = self.l.search(
            settings.LDAP_BASE,ldap.SCOPE_SUBTREE,philter,ret
        )
        result_type, result_data = self.l.result(result_id, 0)

        try:
            r = result_data[0][1]
        except:
            r = None
        return r
