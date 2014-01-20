# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def home(request):

    username = None
    if request.session.get('username'):
        username = request.session['username']
        del request.session['username']

    return render_to_response(
        "core/home.html",{'action':reverse_lazy("auth_login"),},
        context_instance=RequestContext(request)
    )
