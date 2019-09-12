#-- coding: utf-8 --
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from djaludir.core.sql import (
    ACTIVITY_SEARCH, RELATIVES_ORIG, SEARCH
)
from djaludir.manager.utils import (
    clear_privacy, email_differences,
    get_countries, get_majors, get_message_info, get_privacy,
    get_relative, get_states, get_alumna, get_activity, insert_privacy,
    set_activity, set_address, set_alumna, set_relative
)

from djtools.utils.mail import send_mail
from djzbar.utils.informix import do_sql

from datetime import date

INFORMIX_DEBUG = settings.INFORMIX_DEBUG


@login_required
def display(request, cid):
    # fetch information about the alumna
    alumna = get_alumna(cid)
    if alumna != None:
        activities = get_activity(cid, False)
        athletics = get_activity(cid, True)
        relatives = get_relative(cid)
        privacy = get_privacy(cid)
    else:
        activities = None
        athletics = None
        relatives = None
        privacy = None

    return render(
        request, 'manager/display.html',
        {
            'studentID':cid, 'person':alumna, 'activities':activities,
            'athletics':athletics, 'relatives':relatives, 'privacy':privacy
        }
    )


@login_required
def update(request):

    if request.method=='POST':
        # Retrieve the ID of the alumn(a|us)
        cid = request.POST.get('carthageID')

        user = request.user

        if int(cid) == int(user.id) or user.is_superuser:

            # personal information
            set_alumna(request)

            # relatives
            if request.POST.get('relativeCount'):
                set_relative(request)

            # organizations and athletic involvement
            if request.POST.get('activityCount'):
                set_activity(request, 'activity')

            if request.POST.get('athleticCount'):
                set_activity(request, 'athletic')

            # home and work address information
            set_address(request, 'WORK')
            set_address(request, 'HOME')

            # Clear privacy values
            clear_privacy(cid)

            # Manager privacy settings
            personal = request.POST.get('privacyPersonal','Y')
            insert_privacy(cid, 'Personal', personal)

            family = request.POST.get('privacyFamily','Y')
            insert_privacy(cid, 'Family', family)

            academics = request.POST.get('privacyAcademics','Y')
            insert_privacy(cid, 'Academics', academics)

            professional = request.POST.get('privacyProfessional','Y')
            insert_privacy(cid, 'Professional', professional)

            address = request.POST.get('privacyAddress','Y')
            insert_privacy(cid, 'Address', address)

            # Generate an email specifying the differences between
            # the existing information and the newly submitted data
            response = email_differences(cid, request)

            # the email_differences() returns a response that displays the
            # data rather than sending the email if DEBUG is True, otherwise
            # we redirect the user to the manager edit view
            if not settings.DEBUG:
                response = HttpResponseRedirect(
                    reverse(
                        'manager_user_edit_success', kwargs={'cid':cid}
                    )
                )
        else:
            response = HttpResponse(
                "You do not have permission to manage this profile",
                content_type='text/plain; charset=utf-8'
            )
    else:
        response = HttpResponse(
            "Requires POST", content_type='text/plain; charset=utf-8'
        )

    return response


@login_required
def search(request, messageSent = False, permissionDenied = False):
    # Collection of fieldnames used in search
    fieldlist = []
    # Collection of terms used in search
    terms = []
    # Recordset of the alumni who match the search criteria
    matches = []
    message = ''
    sql = ''
    if request.method == 'POST':
        orSQL = ''
        andSQL = ''
        # Sport/activities are searched via "OR", all other fields are "AND"
        # so assemble the list of fields to run through the logic
        # to create the appropriate filters
        for rowNum in range (0, int(request.POST.get('maxCriteria')) + 1):
            fieldname = request.POST.get('within' + str(rowNum))
            searchterm = request.POST.get('term' + str(rowNum))

            if fieldname is not None and searchterm is not None \
            and searchterm != '':
                fieldlist += (fieldname,)
                terms += (searchterm,)

                if fieldname == 'activity':
                    if len(orSQL) > 0:
                        orSQL += ' OR'
                    orSQL += u' LOWER(invl_table.txt) LIKE "%%{}%%"'.format(
                        searchterm.lower()
                    )
                elif fieldname == 'alum.cl_yr' or fieldname == 'ids.id':
                    if len(andSQL) > 0:
                        andSQL += ' AND'
                    andSQL += u' {} = {}'.format(fieldname, searchterm)
                else:
                    if len(andSQL) > 0:
                        andSQL += ' AND'
                    andSQL += u'''
                        LOWER(TRIM({}::varchar(250))) LIKE "%%{}%%"
                    '''.format(
                        fieldname, searchterm.lower()
                    )

        # Based on the criteria specified by the user,
        # add the necessary tables to the search query
        selectFromSQL = SEARCH
        # If search criteria includes activity or sport
        # add the involvement tables
        if 'activity' in fieldlist:
            selectFromSQL += u'''
                LEFT JOIN involve_rec ON ids.id = involve_rec.id
                LEFT JOIN invl_table ON involve_rec.invl = invl_table.invl
            '''

        # If search criteria includes the student's major
        # QUESTION - Should we check all three major fields
        # for each major specified or is sequence important?
        if 'major1.txt' in fieldlist or 'major2.txt' in fieldlist:
            selectFromSQL += u'''
                LEFT JOIN
                    prog_enr_rec progs
                ON
                    ids.id = progs.id
                AND
                    progs.acst = "GRAD"
            '''
            if 'major1.txt' in fieldlist:
                selectFromSQL += u'''
                    LEFT JOIN major_table major1 ON progs.major1 = major1.major
                '''
            if 'major2.txt' in fieldlist:
                selectFromSQL += u'''
                    LEFT JOIN major_table major2 ON progs.major2 = major2.major
                '''

        # Privacy Settings - only add the restrictions for the fields
        # actually included in the search criteria
        personal = [
            'ids.firstname', 'ids.lastname', 'maiden.lastname',
            'ids.id', 'alum.cl_yr'
        ]
        if bool(set(personal) & set(fieldlist)) == True:
            selectFromSQL += u'''
                LEFT JOIN
                    stg_aludir_privacy per_priv
                ON
                    ids.id = per_priv.id
                AND
                    per_priv.fieldname = "Personal"
            '''
            if len(andSQL) > 0:
                andSQL += ' AND'
            andSQL += u' NVL(per_priv.display, "N") = "N"'

        academics = ['activity', 'major1.txt', 'major2.txt']
        if bool(set(academics) & set(fieldlist)) == True:
            selectFromSQL += u'''
                LEFT JOIN
                    stg_aludir_privacy acad_priv
                ON
                    ids.id = acad_priv.id
                AND
                    acad_priv.fieldname = "Academics"
            '''
            if len(andSQL) > 0:
                andSQL += ' AND'
            andSQL += u' NVL(acad_priv.display, "N") = "N"'

        professional = ['job_title']
        if bool(set(professional) & set(fieldlist)) == True:
            selectFromSQL += u'''
                LEFT JOIN
                    stg_aludir_privacy pro_priv
                ON
                    ids.id = pro_priv.id
                AND
                    pro_priv.fieldname = "Professional"
            '''
            if len(andSQL) > 0:
                andSQL += ' AND'
            andSQL += u' NVL(pro_priv.display, "N") = "N"'

        address = ['home_city', 'home_state']
        if bool(set(address) & set(fieldlist)) == True:
            selectFromSQL += u'''
                LEFT JOIN
                    stg_aludir_privacy add_priv
                ON
                    ids.id = add_priv.id
                AND
                    add_priv.fieldname = "Address"
            '''
            if len(andSQL) > 0:
                andSQL += ' AND'
            andSQL += u' NVL(add_priv.display, "N") = "N"'

        # If search criteria were submitted, flesh out the sql query.
        # Include "and's", "or's" and sorting
        if len(andSQL + orSQL) > 0:
            if len(orSQL) > 0:
                orSQL = u'({})'.format(orSQL)
            if len(andSQL) > 0 and len(orSQL) > 0:

                andSQL = u' AND {}'.format(andSQL)
            sql = u'''
                {}
                WHERE
                    {} {}
                AND
                    holds.hld_no IS NULL
                GROUP BY
                    class_year, fname, aname, maiden_name, lastname, id,
                    email, sort1, sort2
                ORDER BY
                    lastname, fname, alum.cl_yr
            '''.format(selectFromSQL, orSQL, andSQL)

            objs = do_sql(sql, INFORMIX_DEBUG)

            if objs:
                matches = objs.fetchall()

    if messageSent == True:
        message = "Your message was sent successfully!"

    if permissionDenied == True:
        message = "You do not have permission to edit this record."

    return render(
        request, 'manager/search.html', {
            'message':message, 'searching':dict(zip(fieldlist, terms)),
            'matches':matches, 'debug':sql
        }
    )


@login_required
def edit(request, cid, success = False):
    if int(cid) == int(request.user.id) or request.user.is_superuser:
        # Retrieve relevant information about the alumna
        alumna = get_alumna(cid)
        activities = get_activity(cid, False)
        athletics = get_activity(cid, True)
        relatives = get_relative(cid)
        privacy = get_privacy(cid)

        # Assemble collections for the user to make choices
        majors = get_majors()
        prefixes = dict([
            ('',''),('DR','Dr'),('MR','Mr'),('MRS','Mrs'),
            ('MS','Ms'),('Miss','Miss'),('REV','Rev')
        ])
        suffixes = ('','II','III','IV','JR','MD','PHD','SR')
        year_range = range(1900, date.today().year + 1)
        relationships = settings.RELATIONSHIPS
        states = get_states()
        countries = get_countries()

        return render(
            request,
            'manager/edit.html', {
                'submitted':success,'studentID':cid, 'person':alumna,
                'activities':activities, 'athletics':athletics,
                'relatives':relatives, 'privacy':privacy, 'majors':majors,
                'prefixes':prefixes, 'suffixes':suffixes,
                'years':year_range, 'relationships':relationships,
                'states':states, 'countries':countries
            }
        )
    else:
        return HttpResponseRedirect(reverse('manager_search_denied'))


@login_required
def message(request, cid, recipientHasEmail = True):
    recipient = get_message_info(cid)
    recipientHasEmail = len(recipient.email) > 0
    return render(
        request,
        'manager/create_message.html', {
            'validRecipient':recipientHasEmail, 'recipient':recipient
        }
    )


@login_required
def send_message(request):
    recipient_id = request.POST.get('recipientID')
    recipient = get_message_info(recipient_id)

    attachEmail = request.POST.get('addEmail', 'N')
    emailBody = request.POST.get('emailBody')

    sender = get_message_info(request.user.id)

    # If the inforamation about the sender is unavailable,
    # create empty/default values
    if sender == None or len(sender) == 0:
        sender = {
            'id':0,
            'email':settings.DEFAULT_FROM_EMAIL,
            'firstname':'a',
            'lastname':'friend',
        }

    autoAddOn = ''
    if attachEmail == 'Y':
        autoAddOn = 'Y'

    # Initialize necessary components to generate email
    data = {
        'body':emailBody,'recipient':recipient,'auto':autoAddOn,'sender':sender
    }

    subject = u"Message from {} {} via the Carthage Alumni Directory".format(
        sender.firstname, sender.lastname
    )
    send_mail(
        request, [recipient.email,], subject, sender.email,
        'manager/send_message.html', data, settings.MANAGERS
    )

    # Reuse the search page
    return HttpResponseRedirect(
        reverse('manager_search_sent', kwargs={'messageSent':True})
    )


@login_required
def search_activity(request):
    search_string = request.GET.get('term','Soccer')
    objs = do_sql(
        ACTIVITY_SEARCH(search_string = search_string.lower()), INFORMIX_DEBUG
    )

    return HttpResponse(objs.fetchall())
