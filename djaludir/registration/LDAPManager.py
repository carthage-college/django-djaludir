# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied

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

    def bind(self, dn, password):

        # Attempt to bind to the user's DN.
        # we need try/except here for edge cass errors
        # like server refuses to execute.
        """
        try:
            self.l.simple_bind_s(dn,password)
        except:
            raise PermissionDenied
        """
        self.l.simple_bind_s(dn,password)

    def create(self, person):
        """
        Creates a new LDAP user.
        Takes as argument a dictionary with the following key/value pairs:

        objectclass                 ["User","carthageUser"]
        givenName                   [first name]
        sn                          [last name]
        carthageDob                 [date of birth]
        carthageNameID              [college ID]
        cn                          [we use email for username]
        mail                        [email]
        userPassword                [password]
        carthageFacultyStatus       [faculty]
        carthageStaffStatus         [staff]
        carthageStudentStatus       [student]
        carthageFormerStudentStatus [alumni]
        carthageOtherStatus         [trustees etc]
        """
        user = modlist.addModlist(person)

        dn = 'cn=%s,o=USERS' % (person["mail"])
        self.l.add_s(dn, user)
        return self.search(person["carthageNameID"])

    def dj_create(self, username, data):
        # We create a User object for LDAP users so we can get
        # permissions, however we -don't- want them to be able to
        # login without going through LDAP with this user. So we
        # effectively disable their non-LDAP login ability by
        # setting it to a random password that is not given to
        # them. In this way, static users that don't go through
        # ldap can still login properly, and LDAP users still
        # have a User object.

        from random import choice
        import string
        temp_pass = ""
        data = data[0][1]
        for i in range(48):
            temp_pass = temp_pass + choice(string.letters)
        email = data['mail'][0]
        if not email:
            email = username
        user = User.objects.create_user(username,email,temp_pass)
        user.first_name = data['givenName'][0]
        user.last_name = data['sn'][0]
        user.save()
        # add to groups
        for key, val in settings.LDAP_GROUPS.items():
            group = data.get(key)
            if group and group[0] == 'A':
                g = Group.objects.get(name__iexact=key)
                g.user_set.add(user)
        return user

    def update(self, person):
        """
        Updates an LDAP user.
        """
        return None

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
        Returns a list with dn tuple and a dictionary with the
        following key/value pairs:

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
        ret = settings.LDAP_RETURN

        result_id = self.l.search(
            settings.LDAP_BASE,ldap.SCOPE_SUBTREE,philter,ret
        )
        result_type, result_data = self.l.result(result_id, 0)
        # If the user does not exist in LDAP, Fail.
        if (len(result_data) != 1):
            return None
        else:
            return result_data

