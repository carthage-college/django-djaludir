# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm

class MyForm(forms.ModelForm):

    class Meta:
        model = MyModel

