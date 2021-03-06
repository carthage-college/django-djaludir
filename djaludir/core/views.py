# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    username = None
    if request.session.get('username'):
        username = request.session['username']
        del request.session['username']

    message = False
    if 'ldap_password_success' in request.session:
        del request.session['ldap_password_success']
        message = """
            You have successfully changed your password, and are now logged in.
        """

    return render(
        request, 'core/home.html',
        {'action':reverse_lazy('auth_login'),'message':message}
    )
