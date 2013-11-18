# -*- coding: utf-8 -*-
from django import forms

from djaludir.registration.LDAPManager import LDAPManager

class RegistrationSearchForm(forms.Form):

    givenName      = forms.CharField(required=True,max_length=64)
    sn             = forms.CharField(required=True,max_length=64)
    #carthageDob     = forms.DateField(required=True, help_text="Format: mm/dd/yyyy")
    carthageDob    = forms.DateField(required=False, help_text="Format: mm/dd/yyyy")
    #postal_code     = forms.CharField(required=True,max_length=10)
    postal_code     = forms.CharField(required=False,max_length=10)
    carthageNameID  = forms.CharField(required=False,max_length=8)
    mail           = forms.EmailField(required=False,max_length=128)
    alumna          = forms.CharField(required=False,max_length=8)
    ldap_name       = forms.CharField(required=False,max_length=32)

class CreateLdapForm(forms.Form):

    givenName       = forms.CharField(required=True,max_length=64, label="First name")
    sn              = forms.CharField(required=True,max_length=64, label="Last name")
    mail            = forms.EmailField(required=True,max_length=128, label="Email")
    carthageDob     = forms.DateField(required=True, label="Date of birth", help_text="Format: mm/dd/yyyy")
    carthageNameID  = forms.CharField(required=True,max_length=8, label="College ID", widget=forms.HiddenInput())
    userPassword    = forms.CharField(required=True,max_length=64, label="Password", widget=forms.PasswordInput(), help_text="Minimum 8 characters.")
    confPassword    = forms.CharField(required=True,max_length=64, label="Confirm password", widget=forms.PasswordInput())

    def clean_userPassword(self):
        if len(self.cleaned_data.get("userPassword")) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return cleaned_data["userPassword"]

    def clean_confPassword(self):
        cleaned_data = self.cleaned_data
        p1 = cleaned_data.get("userPassword")
        p2 = cleaned_data.get("confPassword")
        if p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data["confPassword"]

    def clean_mail(self):
        cleaned_data = self.cleaned_data
        l = LDAPManager()
        user = l.search(cleaned_data.get("mail"),field="cn")
        if user:
            raise forms.ValidationError("That email already exists in the system. Use another.")
        return cleaned_data["mail"]

