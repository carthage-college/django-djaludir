# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from djaludir.core.models import YEARS

def search(request):
    return render_to_response(
        "registration/search.html",
        {'years':YEARS,},
        context_instance=RequestContext(request)
    )
