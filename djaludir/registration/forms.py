# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings

from djauth.LDAPManager import LDAPManager
from djtools.fields.validators import validate_epoch


class RegistrationSearchForm(forms.Form):

    givenName = forms.CharField(
        required=True,max_length=64
    )
    sn = forms.CharField(
        required=True,max_length=64
    )
    carthageDob = forms.DateField(
        required=True,
        validators=[validate_epoch],
        help_text="Format: mm/dd/yyyy",
    )
    postal_code = forms.CharField(
        required=False,max_length=10
    )
    carthageNameID = forms.CharField(
        required=False,max_length=8
    )
    mail = forms.EmailField(
        required=False,max_length=128
    )
    alumna = forms.CharField(
        required=False,max_length=8
    )
    ldap_name = forms.CharField(
        required=False,max_length=32
    )

class CreateLdapForm(forms.Form):

    givenName = forms.CharField(
        label="First name",
        required=True, max_length=64
    )
    sn = forms.CharField(
        label="Last name",
        required=True, max_length=64
    )
    mail = forms.EmailField(
        label="Email",
        required=True, max_length=128
    )
    carthageDob = forms.DateField(
        label="Date of birth", required=True,
        validators=[validate_epoch],
        help_text="Format: mm/dd/yyyy"
    )
    carthageNameID = forms.CharField(
        label="College ID", required=True, max_length=8,
        widget=forms.HiddenInput()
    )
    userPassword = forms.CharField(
        label="Password", required=True, max_length=64,
        widget=forms.PasswordInput(),
        help_text="""
            Minimum 12 characters and at least one lowercase letter
            and one number.
        """
    )
    confPassword = forms.CharField(
        label="Confirm password", required=True, max_length=64,
        widget=forms.PasswordInput()
    )

    def clean_userPassword(self):
        import re
        pw = self.cleaned_data.get('userPassword')
        if len(pw) < 12:
            raise forms.ValidationError(
                """
                Password must be at least 12 characters.
                """
            )

        if not re.search('[a-z]+',pw) or not re.search('[0-9]+', pw):
            raise forms.ValidationError(
                """
                Your password must include at least one lowercase letter
                and at least one number.
                """
            )
        return self.cleaned_data.get('userPassword')

    def clean_confPassword(self):
        cleaned_data = self.cleaned_data
        p1 = cleaned_data.get('userPassword')
        p2 = cleaned_data.get('confPassword')
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data['confPassword']

    def clean_mail(self):
        cleaned_data = self.cleaned_data
        l = LDAPManager(
            protocol=settings.LDAP_PROTOCOL_PWM,
            server=settings.LDAP_SERVER_PWM,
            port=settings.LDAP_PORT_PWM,
            user=settings.LDAP_USER_PWM,
            password=settings.LDAP_PASS_PWM,
            base=settings.LDAP_BASE_PWM
        )
        user = l.search(cleaned_data.get('mail'),field='cn')
        if user:
            raise forms.ValidationError(
                "That email already exists in the system. Use another."
            )
        return cleaned_data['mail']

class ModifyLdapPasswordForm(forms.Form):
    """
    modify a user's ldap password
    """
    cn = forms.CharField(
        required=True,
        max_length=128, label="Carthage Username"
    )
    sn = forms.CharField(
        required=True,
        max_length=64, label="Your Last name"
    )
    ssn = forms.CharField(
        required=True,
        max_length=4,
        label="Last four digits of your Social Security Number"
    )
    carthageDob = forms.DateField(
        required=True,
        validators=[validate_epoch],
        label="Date of birth",
        help_text="Format: mm/dd/yyyy"
    )
    userPassword = forms.CharField(
        required=True,
        max_length=64, label="Password",
        widget=forms.PasswordInput(),
        help_text="""
            Minimum 12 characters and at least one letter and one number.
        """
    )
    confPassword = forms.CharField(
        required=True,
        max_length=64, label="Confirm password",
        widget=forms.PasswordInput()
    )

    def clean_userPassword(self):
        import re
        pw = self.cleaned_data.get('userPassword')
        if len(pw) < 12:
            raise forms.ValidationError(
                "Password must be at least 12 characters."
            )

        if not re.search('[a-zA-Z]+', pw) or not re.search('[0-9]+', pw):
            raise forms.ValidationError(
                u'Your password must include at least \
                  one letter and at least one number.'
            )
        return self.cleaned_data.get('userPassword')

    def clean_confPassword(self):
        cleaned_data = self.cleaned_data
        p1 = cleaned_data.get('userPassword')
        p2 = cleaned_data.get('confPassword')
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data['confPassword']
