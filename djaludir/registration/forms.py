# -*- coding: utf-8 -*-
from django import forms

class RegistrationSearchForm(forms.Form):

    first_name      = forms.CharField(required=True,max_length=64)
    last_name       = forms.CharField(required=True,max_length=64)
    previous_name   = forms.CharField(required=False,max_length=64)
    email           = forms.EmailField(required=False,max_length=128)
    college_id      = forms.CharField(required=False,max_length=8)
    dob             = forms.DateField(required=False)
    year_start      = forms.CharField(required=False,max_length=4)
    year_end        = forms.CharField(required=False,max_length=4)


