# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User, Group

from djaludir.core.models import YEARS
from djaludir.registration import SEARCH, SEARCH_GROUP_BY, SEARCH_ORDER_BY
from djaludir.registration import CONFIRM_USER
from djaludir.registration.forms import RegistrationSearchForm
from djaludir.registration.forms import CreateLdapForm
from djaludir.registration.forms import ModifyLdapPasswordForm
from djaludir.auth.backends import LDAPBackend

from djzbar.utils.informix import do_sql
from djtools.utils.mail import send_mail
from djauth.LDAPManager import LDAPManager

TO_LIST = ["larry@carthage.edu",]

import logging
logger = logging.getLogger(__name__)

def error_mess(val):
    error = '''
        %s results returned. Please try your search again,
        or contact the
        <a href="mailto:alumnioffice@carthage.edu">Alumni Office</a>
        for further assistance.
    ''' % val
    return error

def search_home(request):
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
        xsql = None
        form = RegistrationSearchForm(request.POST)
        if form.is_valid():
            # data dictionary
            data = form.cleaned_data
            where = (' ( lower(id_rec.firstname) like "%%%s%%" OR'
                ' lower(aname_rec.line1) like "%%%s%%" )'
                % (data["givenName"].lower(),data["givenName"].lower()))
            where += ' AND'
            where += ' ( lower(id_rec.lastname) = "%s" )' % data['sn'].lower()
            # if we have ID, we don't need anything else
            if data["carthageNameID"]:
                where+= 'AND id_rec.id = "%s"' % data["carthageNameID"]
            else:
                where+= ' AND'
                where+= '''
                     (profile_rec.birth_date = "%s"
                ''' % data["carthageDob"].strftime("%m/%d/%Y")
                where+= ' OR profile_rec.birth_date is null)'
                if data["postal_code"]:
                    where+= ' AND'
                    where+= '''
                        ( id_rec.zip like "%%%s%%" or NVL(id_rec.zip,"") = "" )
                    ''' % data["postal_code"]
            xsql = SEARCH + where
            xsql += SEARCH_GROUP_BY
            xsql += SEARCH_ORDER_BY
            results = do_sql(xsql, key=settings.INFORMIX_DEBUG)

            objects = results.fetchall()
            ln = len(objects)
            if ln < 1:
                results = None
                error = error_mess("No")
            elif ln > 10:
                results = None
                error = error_mess(ln)
            else:
                results = objects
        else:
            error = form.errors
        extra_context = {'form':form,'error':error,'results':results,'sql':xsql,}
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
            # search ldap
            l = LDAPManager()
            user = l.search(data["alumna"])
            if user:
                # we have a user
                user = user[0][1]
                # update informix if no ldap_user
                if not settings.DEBUG and data["ldap_name"] == '':
                    sql = """
                        UPDATE cvid_rec SET ldap_name='%s' WHERE cx_id = '%s'
                    """ % (user["cn"][0], data["alumna"])
                    results = do_sql(sql, key=settings.INFORMIX_DEBUG)
                # check for challenge questions
                l = LDAPBackend()
                request.session['ldap_questions'] = l.get_questions(user["cn"][0])
                # display the login form
                form = {'data':{'username':user["cn"][0],}}
                redir = reverse_lazy("alumni_directory_home")
                extra_context = {
                    'user':user,'form':form,
                    'next':redir,'action':settings.LOGIN_URL
                }
                template = "login"
            else:
                # display the create form
                data["carthageNameID"] = data["alumna"]
                request.session['ldap_name'] = data.get("ldap_name")
                form = CreateLdapForm(initial=data)
                action = reverse_lazy("registration_create_ldap")
                extra_context = {'action':action,'form':form,}
                template = "create"
            return render_to_response(
                "registration/%s_ldap.inc.html" % template, extra_context,
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
            # dob format: YYYY-MM-DD
            data["carthageDob"] = data["carthageDob"].strftime("%Y-%m-%d")
            if request.session.get('ldap_name') != "":
                # username (cn) will be ldap_name from informix
                data["cn"] = request.session['ldap_name']
            else:
                # username (cn) will be email address
                data["cn"] = data["mail"]
            # remove confirmation password
            data.pop('confPassword',None)
            # python ldap wants strings, not unicode
            for k,v in data.items():
                data[k] = str(v)
            data["objectclass"] = settings.LDAP_OBJECT_CLASS_LIST
            data["carthageFacultyStatus"] = ""
            data["carthageStaffStatus"] = ""
            data["carthageStudentStatus"] = ""
            data["carthageFormerStudentStatus"] = "A"
            data["carthageOtherStatus"] = ""
            # create the ldap user
            l = LDAPManager()
            user = l.create(data)
            # set session ldap_cn, why?
            request.session['ldap_cn'] = user[0][1]["cn"][0]
            if not settings.DEBUG and request.session.get('ldap_name') != "":
                # update informix cvid_rec.ldap_user
                sql = """
                    UPDATE cvid_rec SET ldap_name='%s' WHERE cx_id = '%s'
                """ % (user[0][1]["cn"][0],user[0][1]["carthageNameID"])
                ln = do_sql(sql, key=settings.INFORMIX_DEBUG)
            else:
                logger.debug("data = %s" % data)
            # create the django user
            djuser = l.dj_create(user)
            # authenticate user
            djuser.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, djuser)
            # send email to admins
            subject = "[LDAP][Create] %s %s" % (
                user[0][1]["givenName"][0],
                user[0][1]["sn"][0]
            )
            send_mail(
                request,TO_LIST, subject, data["mail"],
                "registration/create_ldap_email.html", data
            )
            return HttpResponseRedirect(reverse_lazy("alumni_directory_home"))
        else:
            return render_to_response(
                "registration/create_ldap.html", {'form':form,},
                context_instance=RequestContext(request)
            )
    elif settings.DEBUG:
        form = CreateLdapForm(initial={"carthageNameID":'901257',})
        return render_to_response(
            "registration/create_ldap.html", {'form':form,},
            context_instance=RequestContext(request)
        )
    else:
        # POST required
        return HttpResponseRedirect(reverse_lazy("registration_search"))

def modify_ldap_password(request):
    """
    Modifies the password for an LDAP account.
    Requires POST.
    """
    errors = {}
    if request.method == "POST":
        form = ModifyLdapPasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            where = 'WHERE'
            where+= ' ( lower(id_rec.lastname) = "%s" )' % data['sn'].lower()
            where+= ' AND'
            where+= '''
                 (profile_rec.birth_date = "%s"
            ''' % data["carthageDob"].strftime("%m/%d/%Y")
            where+= ' OR profile_rec.birth_date is null)'
            where+= ' AND'
            where+= '''
                SUBSTRING(id_rec.ss_no FROM 8 FOR 4) = "%s"
            ''' % data["ssn"]
            sql = CONFIRM_USER + where
            results = do_sql(sql, key=settings.INFORMIX_DEBUG)
            objects = results.fetchall()
            if len(objects) == 1:
                # initial the ldap manager

                l = LDAPManager(
                    protocol=settings.LDAP_PROTOCOL_PWM,
                    server=settings.LDAP_SERVER_PWM,
                    port=settings.LDAP_PORT_PWM,
                    user=settings.LDAP_USER_PWM,
                    password=settings.LDAP_PASS_PWM,
                    base=settings.LDAP_BASE_PWM
                )

                search = l.search(objects[0].id)
                if search:
                    # now modify password
                    # modify_s() returns a tuple with status code
                    # and an empty list: (103, [])
                    status = l.modify(search[0][0],"userPassword",data["userPassword"])
                    # success = 103
                    if status[0] == 103:
                        # success
                        request.session['ldap_password_success'] = True
                        # Get the user record or create one with no privileges.
                        try:
                            user = User.objects.get(username__exact=search[0][1]["cn"][0])
                        except:
                            # Create a User object.
                            user = l.dj_create(search)
                        # authenticate user
                        user.backend = 'django.contrib.auth.backends.ModelBackend'
                        login(request, user)
                        return HttpResponseRedirect(reverse_lazy("alumni_directory_home"))
                    else:
                        # fail
                        errors["ldap"] = "We failed to update your password."
                else:
                    errors["ldap"] = "We failed to find your Alumni account."
            else:
                errors["informix"] = "We could not find you in the database."
    else:
        form = ModifyLdapPasswordForm()

    return render_to_response(
        "registration/modify_ldap_password.html", {'form':form,'errors':errors},
        context_instance=RequestContext(request)
    )
