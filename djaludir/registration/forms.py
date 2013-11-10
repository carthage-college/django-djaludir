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


