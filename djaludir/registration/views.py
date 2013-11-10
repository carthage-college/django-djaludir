# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djaludir.core.models import YEARS
from djaludir.registration import SEARCH
from djaludir.registration.forms import RegistrationSearchForm

from djzbar.utils.informix import do_sql

def search(request):
    earl = reverse_lazy("search_informix_ajax")
    return render_to_response(
        "registration/search.html",
        {'years':YEARS,'ajax_earl':earl,},
        context_instance=RequestContext(request)
    )

def search_informix_ajax(request):
    if request.method == "POST":
        results = None
        error = None
        form = RegistrationSearchForm(request.POST)
        if form.is_valid():
            # data dictionary
            data = form.cleaned_data
            where = (' ( lower(id_rec.firstname) like "%%%s%%" OR'
                     ' lower(aname_rec.line1) like "%%%s%%" )'
                     % (data["first_name"],data["first_name"]))
            where += ' AND'
            where += ' lower(id_rec.lastname) = "%s"' % data['last_name'].lower()
            if data["dob"]:
                where+= ' AND'
                where+= ' (profile_rec.birth_date = "%s"' % data["dob"].strftime("%m/%d/%Y")
                where+= ' OR profile_rec.birth_date is null)'
            if data["postal_code"]:
                where+= ' AND'
                where+= ' ( id_rec.zip like "%%%s%%" or NVL(id_rec.zip,"") = "" )' % data["postal_code"]
            if data["college_id"]:
                where+= ' AND'
                where+= ' id_rec.id = "%s"' % data["college_id"]
            xsql = SEARCH + where
            xsql += ' ORDER BY id_rec.lastname, id_rec.firstname, profile_rec.birth_date'
            results = do_sql(xsql)
            objects = []
            if results:
                for r in results:
                    objects.append(r)
                if len(objects) < 1:
                    results = None
                    error = "No results returned."
                    #error = xsql
                #elif len(objects) > 10:
                #    results = None
                #    error = "Too many results returned. Narrow your search."
                else:
                    results = objects
            else:
                error = xsql
        else:
            error = form.errors
            xsql = None
        extra_context = {'form':form,'error':error,'results':results,'sql':xsql,}
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
