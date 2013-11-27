import ldap

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from djaludir.registration.LDAPManager import LDAPManager

import logging
logger = logging.getLogger(__name__)

class LDAPBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        if not password:
            return None
        username = username.lower()
        base = settings.LDAP_BASE
        scope = ldap.SCOPE_SUBTREE
        philter = """
            (&(objectclass=%s) (cn=%s))
        """ % (settings.LDAP_OBJECT_CLASS,username)
        ret = settings.LDAP_RETURN

        l = LDAPManager()

        try:
            result_data = l.search(username,field="cn")

            # If the user does not exist in LDAP, Fail.
            if not result_data:
                return None

            # Attempt to bind to the user's DN.
            l.bind(result_data[0][0],password)

            # The user existed and authenticated.
            # Get the user record or create one with no privileges.
            try:
                user = User.objects.get(username__exact=username)
            except:
                # Create a User object.
                user = l.dj_create(username,result_data)

            # Success.
            return user
        except ldap.INVALID_CREDENTIALS:
            # Name or password were bad. Fail permanently.
            #raise PermissionDenied
            return None

    def get_user(self, user_id):
        """
        OJO: needed for django auth, don't delete
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
