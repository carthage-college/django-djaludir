# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

from djaludir.core.models import YEARS
from djaludir.registration import SEARCH
from djaludir.registration.forms import RegistrationSearchForm, CreateLdapForm
from djaludir.registration.LDAPManager import LDAPManager

from djzbar.utils.informix import do_sql
from djtools.utils.mail import send_mail

TO_LIST = ["larry@carthage.edu",]

import logging
logger = logging.getLogger(__name__)

def search(request):
    """
    Search home, from where we begin the search for an alumna's
    record in Informix and then in LDAP.
    """
    informix_earl = reverse_lazy("registration_search_informix")
    ldap_earl = reverse_lazy("registration_search_ldap")
    return render_to_response(
        "registration/search.html",
        {'informix_earl':informix_earl,'ldap_earl':ldap_earl},
        context_instance=RequestContext(request)
    )

def search_informix(request):
    """
    Search informix database for alumna's record.
    Requires POST, which is sent as Ajax request.
    Returns a list of possible candidates.
    """
    if request.method == "POST":
        results = None
        error = None
        form = RegistrationSearchForm(request.POST)
        if form.is_valid():
            # data dictionary
            data = form.cleaned_data
            where = (' ( lower(id_rec.firstname) like "%%%s%%" OR'
                     ' lower(aname_rec.line1) like "%%%s%%" )'
                     % (data["givenName"],data["givenName"]))
            where += ' AND'
            where += ' lower(id_rec.lastname) = "%s"' % data['sn'].lower()
            if data["carthageDob"]:
                where+= ' AND'
                where+= ' (profile_rec.birth_date = "%s"' % data["carthageDob"].strftime("%m/%d/%Y")
                where+= ' OR profile_rec.birth_date is null)'
            if data["postal_code"]:
                where+= ' AND'
                where+= ' ( id_rec.zip like "%%%s%%" or NVL(id_rec.zip,"") = "" )' % data["postal_code"]
            if data["carthageNameID"]:
                where+= ' AND'
                where+= ' id_rec.id = "%s"' % data["carthageNameID"]
            xsql = SEARCH + where
            xsql += ' GROUP by id,birth_date,firstname,lastname,alt_name,addr_line1,addr_line2,city,st,postal_code,phone,email,ldap_name'
            xsql += ' ORDER BY id_rec.lastname, id_rec.firstname, profile_rec.birth_date'
            results = do_sql(xsql)
            objects = []
            if results:
                for r in results:
                    objects.append(r)
                if len(objects) < 1:
                    results = None
                    error = '''
                        No results returned. Please try your search again,
                        or contact the
                        <a href="mailto:alumnioffice@carthage.edu">Alumni Office</a>
                        for further assistance.
                    '''
                elif len(objects) > 5:
                    results = None
                    error = "Too many results returned. Narrow your search."
                else:
                    results = objects
            else:
                error = '''
                    No results returned. Please try your search again,
                    or contact the
                    <a href="mailto:alumnioffice@carthage.edu">Alumni Office</a>
                    for further assistance.
                '''
        else:
            error = form.errors
        extra_context = {'form':form,'error':error,'results':results,}
        return render_to_response(
            "registration/search_informix.html", extra_context,
            context_instance=RequestContext(request)
        )
    else:
        # POST required
        return HttpResponseRedirect(reverse_lazy("registration_search"))

def search_ldap(request):
    """
    Search the LDAP store for an alumna's record.
    POST required, which is sent via Ajax request.
    If we find a record, we check Informix to see
    if we have their LDAP username stored, and
    update it if not. Lastly, display login form.
    If no record, allow the user to create one.
    """
    if request.method == "POST":
        form = RegistrationSearchForm(request.POST)
        if form.is_valid():
            # data dictionary
            data = form.cleaned_data
            logger.debug("data = %s" % data)
            l = LDAPManager()
            user = l.search(data["alumna"])
            if user:
                # update informix if no ldap_user
                if not data["ldap_name"] and not settings.DEBUG:
                    sql = """
                        UPDATE cvid_rec SET ldap_name='%s' WHERE cx_id = '%s'"
                    """ % (user["cn"][0],data["alumna"])
                    ln = do_sql(sql)
                else:
                    logger.debug("user = %s" % user)
                # display the login form
                form = {'data':{'username':user["cn"][0],},}
                redir = reverse_lazy("manager_search")
                extra_context = {'user':user,'form':form,'next':redir,}
                template = "login"
            else:
                # display the create form
                data["carthageNameID"] = data["alumna"]
                form = CreateLdapForm(initial=data)
                action = reverse_lazy("registration_create_ldap")
                extra_context = {'action':action,'form':form,}
                template = "create"
            return render_to_response(
                "registration/%s_ldap.html" % template, extra_context,
                context_instance=RequestContext(request)
            )
    else:
        # POST required
        # or doing something nefarious
        return HttpResponseRedirect(reverse_lazy("registration_search"))

def create_ldap(request):
    """
    Creates an LDAP account.
    Requires POST.
    After successful create, we update Informix with
    the LDAP username.
    """
    if request.method == "POST":
        form = CreateLdapForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data["objectclass"] = '["User","carthageUser"]'
            data["cn"] = data["mail"]
            # dob format: YYYY-MM-DD
            data["carthageDob"] = data["carthageDob"].strftime("%Y-%m-%d")
            if not settings.DEBUG:
                # create the ldap user
                l = LDAPManager()
                user = l.create(data)
                # update informix cvid_rec.ldap_user
                sql = """
                    UPDATE cvid_rec SET ldap_name='%s' WHERE cx_id = '%s'"
                """ % (user["cn"][0],data["mail"])
                ln = do_sql(sql)
                # send email to admins
                subject = "[LDAP][Create] %s %s" % (user.givenName,user.sn)
                send_mail(
                    request,TO_LIST, subject, data["email"],
                    "registration/ldap_email.html", data
                )
            else:
                logger.debug("data = %s" % data)
            return HttpResponseRedirect(reverse_lazy("auth_login"))
        else:
            return render_to_response(
                "registration/create.html", {'form':form,},
                context_instance=RequestContext(request)
            )
    else:
        # POST required
        return HttpResponseRedirect(reverse_lazy("registration_search"))
