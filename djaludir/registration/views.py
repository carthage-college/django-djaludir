# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djaludir.core.models import YEARS
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
        form = RegistrationSearchForm(request.POST)
        if form.is_valid():
            # data dictionary
            data = form.cleaned_data
            sql = """
            SELECT
                id_rec.id, profile_rec.birth_date,
                id_rec.firstname,
                id_rec.lastname, aname_rec.line1 as alt_name,id_rec.addr_line1,
                id_rec.addr_line2, id_rec.city, id_rec.st, id_rec.zip,
                id_rec.phone as homephone,
                email_rec.line1 as email
            FROM
                id_rec
            LEFT JOIN
                profile_rec on id_rec.id = profile_rec.id
            LEFT JOIN aa_rec as aname_rec on
                (id_rec.id = aname_rec.id AND aname_rec.aa = "ANDR")
            LEFT JOIN aa_rec as email_rec on
                (id_rec.id = email_rec.id AND email_rec.aa = "EML1")
            WHERE
            """
            where =  ' lower(id_rec.firstname)="%s"' % data['first_name'].lower()
            where += ' AND'
            where += ' lower(id_rec.lastname)="%s"' % data['last_name'].lower()
            xsql = sql + where
            xsql += 'ORDER BY id_rec.lastname'
            results = do_sql(xsql)
            objects = []
            for r in results:
                objects.append(r)
            if len(objects) < 1:
                results = None
            else:
                results = objects
        else:
            results = form.errors
        extra_context = {'results':results,}
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
