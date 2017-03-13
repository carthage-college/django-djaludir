import ldap

from django.conf import settings
from django.contrib.auth.models import User

from djauth.LDAPManager import LDAPManager

import logging
logger = logging.getLogger(__name__)

class LDAPBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_questions(self, cn=None):
        """
        check to see whether or not the user has her
        challenge question & answers set.
        not the best place for this, but for now it will do.
        """
        l = LDAPManager(
            protocol=settings.LDAP_PROTOCOL_PWM,
            server=settings.LDAP_SERVER_PWM,
            port=settings.LDAP_PORT_PWM,
            user=settings.LDAP_USER_PWM,
            password=settings.LDAP_PASS_PWM,
            base=settings.LDAP_BASE_PWM
        )

        result = l.search(cn,field="cn",ret=settings.LDAP_RETURN_PWM)

        try:
            questions = result[0][1][settings.LDAP_CHALLENGE_ATTR][0]
            return True
        except:
            return False

    def authenticate(self, username=None, password=None, request=None):
        if not password:
            return None
        username = username.lower()

        l = LDAPManager()
        '''
        l = LDAPManager(
            protocol=settings.LDAP_PROTOCOL_PWM,
            server=settings.LDAP_SERVER_PWM,
            port=settings.LDAP_PORT_PWM,
            user=settings.LDAP_USER_PWM,
            password=settings.LDAP_PASS_PWM,
            base=settings.LDAP_BASE_PWM
        )
        '''

        try:
            result_data = l.search(username,field="cn")
            # If the user does not exist in LDAP, Fail.
            if not result_data and request:
                request.session['ldap_account'] = False
                return None

            # Attempt to bind to the user's DN.
            l.bind(result_data[0][0],password)
            # Success. The user existed and authenticated.
            # Get the user record or create one with no privileges.
            try:
                user = User.objects.get(username__exact=username)
            except:
                # Create a User object.
                user = l.dj_create(result_data)

            # TODO: update the alumni container
            return user
        except ldap.INVALID_CREDENTIALS:
            # Name or password were bad. Fail permanently.
            request.session['ldap_cn'] = username
            request.session['ldap_account'] = True
            request.session['ldap_questions'] = self.get_questions(username)
            return None

    def get_user(self, user_id):
        """
        OJO: needed for django auth, don't delete
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
