# -*- coding: utf-8 -*-
from django import forms

class RegistrationSearchForm(forms.Form):

    first_name      = forms.CharField(required=True,max_length=64)
    last_name       = forms.CharField(required=True,max_length=64)
    #dob             = forms.DateField(required=True)
    dob             = forms.DateField(required=False)
    #postal_code     = forms.CharField(required=True,max_length=10)
    postal_code     = forms.CharField(required=False,max_length=10)
    college_id      = forms.CharField(required=False,max_length=8)
    #previous_name   = forms.CharField(required=False,max_length=64)
    #email           = forms.EmailField(required=False,max_length=128)
    #year_start      = forms.CharField(required=False,max_length=4)
    #year_end        = forms.CharField(required=False,max_length=4)
    alumna          = forms.CharField(required=False,max_length=8)

class CreateLdapForm(forms.Form):

    givenName       = forms.CharField(required=True,max_length=64, label="First name")
    sn              = forms.CharField(required=True,max_length=64, label="Last name")
    mail            = forms.CharField(required=True,max_length=128, label="Email")
    carthageDob     = forms.DateField(required=True, label="Date of birth")
    carthageNameID  = forms.CharField(required=True,max_length=8, label="College ID")
    userPassword    = forms.CharField(required=True,max_length=64, label="Password")
    confPassword    = forms.CharField(required=True,max_length=64, label="Confirm password")

