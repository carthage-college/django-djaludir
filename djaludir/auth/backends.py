import ldap

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from djaludir.registration.LDAPManager import LDAPManager

class LDAPBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None):
        if not password:
            #raise PermissionDenied
            return None
        username = username.lower()
        base = settings.LDAP_BASE
        scope = ldap.SCOPE_SUBTREE
        philter = "(&(objectclass=carthageUser) (cn=%s))" % username
        ret = settings.LDAP_RETURN

        l = LDAPManager()

        try:
            result_id = l.search(base, scope, philter, ret)
            result_type, result_data = l.result(result_id, 0)
            # If the user does not exist in LDAP, Fail.
            if (len(result_data) != 1):
                return None

            # Attempt to bind to the user's DN.
            # we don't need an "if" statement here.
            # simple_bind will except if it fails, never return a value
            l.simple_bind_s(result_data[0][0],password)

            # The user existed and authenticated.
            # Get the user record or create one with no privileges.

            data = result_data[0][1]
            try:
                user = User.objects.get(username__exact=username)
            except:
                # Create a User object.
                user = l.dj_create(username,data)

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
