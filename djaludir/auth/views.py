# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse

from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

def login_user(request):
    errors = False
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                username=username, password=password, request=request
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(
                        reverse('alumni_directory_home')
                    )
                else:
                    errors = True
            else:
                errors = True
    else:
        form = LoginForm()

    return render(
        request,
        'auth/login.html',{'form': form,'errors':errors}
    )

