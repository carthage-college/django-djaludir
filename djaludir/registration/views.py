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
        results = None
        error = None
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
            where = (' ( lower(id_rec.firstname) like "%%%s%%" OR'
                     ' lower(aname_rec.line1) like "%%%s%%" )'
                     % (data["first_name"],data["first_name"]))
            where += ' AND'
            where += ' lower(id_rec.lastname) = "%s"' % data['last_name'].lower()
            """
            if data["email"]:
                where+= ' AND'
                where+= ' email_rec.line1 = "%s"' % data["email"]
            if data["college_id"]:
                where+= ' AND'
                where+= ' id_rec.id = "%s"' % data["college_id"]
            """
            if data["dob"]:
                where+= ' AND'
                where+= ' profile_rec.birth_date = "%s"' % data["dob"].strftime("%m/%d/%Y")
            #if data["start_year"]:
            #    where+= ' AND'
            #    where+= ' MIN(yr) AS start_year, MAX(yr) AS end_year FROM stu_acad_rec WHERE id = [student_id] AND yr > 0
            xsql = sql + where
            xsql += ' ORDER BY id_rec.lastname, id_rec.firstname, profile_rec.birth_date'
            results = do_sql(xsql)
            objects = []
            if results:
                for r in results:
                    objects.append(r)
                if len(objects) < 1:
                    results = None
                    error = "No results returned."
                elif len(objects) > 5:
                    results = None
                    error = "Too many results returned. Narrow your search."
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
