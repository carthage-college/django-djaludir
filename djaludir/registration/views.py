# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djaludir.core.models import YEARS

def search(request):
    earl = reverse_lazy("registration_search_ajax")
    return render_to_response(
        "registration/search.html",
        {'years':YEARS,'ajax_earl':earl,},
        context_instance=RequestContext(request)
    )

def ajax_ldap_search(request):
    results = "<p>boo!</p>"
    extra_context = {'results':results,}
    if request.method == "POST":
        return render_to_response(
            "registration/search_ajax.html", extra_context,
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse("Post required", content_type="text/plain; charset=utf-8")

def create(request):
    return render_to_response(
        "registration/create.html",
        context_instance=RequestContext(request)
    )
