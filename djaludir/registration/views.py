# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djaludir.core.models import YEARS
from djaludir.registration import SEARCH
from djaludir.registration.forms import RegistrationSearchForm, CreateLdapForm
from djaludir.registration.LDAPManager import LDAPManager
from djzbar.utils.informix import do_sql

def search(request):
    informix_earl = reverse_lazy("registration_search_informix")
    ldap_earl = reverse_lazy("registration_search_ldap")
    return render_to_response(
        "registration/search.html",
        {'years':YEARS,'informix_earl':informix_earl,'ldap_earl':ldap_earl},
        context_instance=RequestContext(request)
    )

def search_informix(request):
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
            xsql += ' GROUP by id,birth_date,firstname,lastname,alt_name,addr_line1,addr_line2,city,st,postal_code,homephone,email,ldap_name'
            xsql += ' ORDER BY id_rec.lastname, id_rec.firstname, profile_rec.birth_date'
            results = do_sql(xsql)
            objects = []
            if results:
                for r in results:
                    objects.append(r)
                if len(objects) < 1:
                    results = None
                    error = "No results returned. Please try your search again, or contact the Alumni Office."
                elif len(objects) > 10:
                    results = None
                    error = "Too many results returned. Narrow your search."
                else:
                    results = objects
            else:
                error = "No results returned. Please try your search again, or contact the Alumni Office."
        else:
            error = form.errors
        extra_context = {'form':form,'error':error,'results':results,}
        return render_to_response(
            "registration/search_informix.html", extra_context,
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse("Post required", content_type="text/plain; charset=utf-8")

def search_ldap(request):
    if request.method == "POST":
        form = RegistrationSearchForm(request.POST)
        if form.is_valid():
            # data dictionary
            data = form.cleaned_data
            l = LDAPManager()
            user = l.search(data["alumna"])
        else:
            error = form.errors
        if user:
            extra_context = {'user':user,}
            template = "search"
        else:
            form = CreateLdapForm()
            extra_context = {'form':form,}
            template = "create"
        return render_to_response(
            "registration/%s_ldap.html" % template, extra_context,
            context_instance=RequestContext(request)
        )
    else:
        return HttpResponse("Post required", content_type="text/plain; charset=utf-8")

def create_ldap(request):
    if request.method == "POST":
        form = CreateLdapForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            l = LDAPManager()
            user = l.create(data)
    else:
        form = CreateLdapForm()
    return render_to_response(
        "registration/create.html", {'form':form,},
        context_instance=RequestContext(request)
    )


