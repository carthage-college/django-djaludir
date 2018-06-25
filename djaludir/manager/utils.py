#-- coding: utf-8 --
from django.conf import settings
from django.shortcuts import render

from djaludir.core.sql import (
    ACTIVITIES, ACTIVITIES_TEMP, ALUMNA, ALUMNA_TEMP, HOMEADDRESS_TEMP,
    MAJORS, PRIVACY, RELATIVES_ORIG, RELATIVES_TEMP, WORKADDRESS_TEMP,
)
from djaludir.core.models import (
    Activity, Address, Alumna, Relative, EXCLUDE_FIELDS
)

from djzbar.utils.informix import do_sql
from djtools.utils.mail import send_mail

import datetime

INFORMIX_DEBUG = settings.INFORMIX_DEBUG

NOW = datetime.datetime.now().strftime('%Y-%m-%d')


def get_alumna(cid):
    """
    Compile all the one-to-one information about the alumn(a|us)
    """

    deceased = 'AND NVL(ids.decsd, "N") = "N"'
    # RIP: alpha
    if settings.DEBUG:
        deceased = ''
    sql = ALUMNA(cid = cid, deceased = deceased)
    student = do_sql(sql, INFORMIX_DEBUG)
    obj = student.fetchone()
    if obj:
        stu = dict(obj)
        # we need to sanitize strings which may contain funky
        # windows characters that informix does not convert to
        # utf-8
        for key, value in stu.iteritems():
            if type(value) is str:
                stu[key] = value.decode('cp1252').encode('utf-8')
        return stu
    else:
        return None


def set_alumna(request):

    user = request.user
    alumna, created = Alumna.objects.get_or_create(user=user, pk=user.id)

    for f in alumna._meta.get_fields():
        field = f.name
        if field not in EXCLUDE_FIELDS:
            setattr(alumna, field, request.POST.get(field))

    alumna.updated_by=(user)
    alumna.save()

    return alumna


def get_activity(cid, is_sports=False):
    """
    Conditional statements to provide the correct logic and
    terminology depending on whether or not activities or athletics
    are returned
    """

    fieldname = 'activity' if not is_sports else 'sport'
    comparison = 'NOT' if not is_sports else ''

    activities_sql = ACTIVITIES(
        cid = cid, fieldname = fieldname, comparison = comparison
    )
    objs = do_sql(activities_sql, INFORMIX_DEBUG)

    return objs.fetchall()


def set_activity(request, tipo):

    user = request.user
    activities = []
    count = '{}Count'.format(tipo)
    for i in range (1, int(request.POST.get(count)) + 1):
        activityText = request.POST.get('{}{}'.format(tipo, str(i)))
        if activityText:
            activity, created = Activity.objects.get_or_create(
                user = user, text = activityText
            )
            activity.updated_by = user
            activity.save()
            activities.append(activity)

    return activities


def get_relative(cid):
    """
    Retrieve collection of relatives (regardless of whether the alumn(a|us)
    is the primary or secondary relationship)
    """

    objs = do_sql(RELATIVES_ORIG(cid = cid), INFORMIX_DEBUG)

    return objs.fetchall()


def set_relative(request):

    user = request.user
    relatives = []
    for i in range (1, int(request.POST.get('relativeCount')) + 1):
        relFname = request.POST.get('relativeFname' + str(i))
        relLname = request.POST.get('relativeLname' + str(i))
        relRelation = request.POST.get('relativeText' + str(i))

        # Because of the way relationships are stored in CX,
        # we must identify if the alumna matches the first or
        # second role in the relationship
        alumPrimary = False
        if(relRelation[-1:] == '1'):
            alumPrimary = True

        if(relRelation[-1:] == '1' or relRelation[-1:] == '2'):
            relRelation = relRelation[0:-1]

        # If the relative has some value in their name and
        # a specified relationship, insert the record
        if (len(relFname + relLname) > 0 and relRelation != ''):
            relative, created = Relative.objects.get_or_create(
                user = user,
                relation_code = relRelation,
                first_name = relFname,
                last_name = relLname
            )
            relative.updated_by = user
            relative.primary = alumPrimary
            relative.save()
            relatives.append(relative)

    return relatives


def get_privacy(cid):
    privacy_sql = PRIVACY(cid = cid)
    privacy = do_sql(privacy_sql, INFORMIX_DEBUG)
    field = []
    setting = []
    for row in privacy:
        field += (row.fieldname,)
        setting += (row.display)
    return dict(zip(field, setting))


def get_majors():
    objs = do_sql(MAJORS, INFORMIX_DEBUG)

    return objs.fetchall()


def get_states():
    states_sql = '''
        SELECT
            TRIM(st) AS st
        FROM
            st_table
        WHERE
            NVL(high_zone, 0) >= 100 ORDER BY TRIM(txt)
    '''
    objs = do_sql(states_sql, INFORMIX_DEBUG)

    return objs.fetchall()


def get_countries():
    countries_sql = '''
        SELECT
            TRIM(ctry) AS ctry, TRIM(txt) AS txt
        FROM
            ctry_table
        ORDER BY
            web_ord, TRIM(txt)
    '''
    objs = do_sql(countries_sql, INFORMIX_DEBUG)

    return objs.fetchall()


def get_message_info(cid):
    message_sql = '''
        SELECT
            ids.id,
            NVL(
                TRIM(email.line1) || TRIM(email.line2) || TRIM(email.line3), ""
            ) AS email,
            TRIM(ids.firstname) AS firstname,
            TRIM(ids.lastname) AS lastname
        FROM
            id_rec ids
        LEFT JOIN
            aa_rec email
        ON
            ids.id = email.id
        AND
            email.aa = "EML2"
        AND
            TODAY BETWEEN email.beg_date
        AND
            NVL(email.end_date, TODAY)
        WHERE
            ids.id = {}
    '''.format(cid)
    message = do_sql(message_sql, INFORMIX_DEBUG)

    return message.fetchone()

def clear_relative(cid):
    sql = '''
        UPDATE
            stg_aludir_relative
        SET
            approved = "N"
        WHERE
            id = {}
        AND
            NVL(approved,"") = ""
    '''.format(cid)
    do_sql(sql, INFORMIX_DEBUG)


def insert_relative(cid, relCode, fname, lname, alumPrimary):
    sql = '''
        INSERT INTO stg_aludir_relative (
            id, relCode, fname, lname, alum_primary, submitted_on
        )
        VALUES
            ({}, '{}', '{}', '{}', '{}', TO_DATE('{}', '%Y-%m-%d'))
    '''.format(
        cid, relCode, fname, lname, alumPrimary, NOW
    )
    do_sql(sql, INFORMIX_DEBUG)
    return sql


def insert_alumni(
    cid, fname, aname, lname, suffix, prefix, email, maidenname, degree,
    class_year, business_name, major1, major2, major3, masters_grad_year,
    job_title
):
    if class_year == '':
        class_year = 0
    if masters_grad_year == '':
        masters_grad_year = 0
    clear_sql = '''
        UPDATE
            stg_aludir_alumni
        SET
            approved = "N"
        WHERE
            id = {}
        AND
            NVL(approved,"") = ""
    '''.format(cid)
    do_sql(clear_sql, INFORMIX_DEBUG)

    if maidenname:
        maidenname = maidenname.replace('(','').replace(')','')

    alumni_sql = '''
        INSERT INTO stg_aludir_alumni (
            id, fname, aname, lname, suffix, prefix, email, maidenname, degree,
            class_year, business_name, major1, major2, major3,
            masters_grad_year, job_title, submitted_on
        )
        VALUES (
            {}, "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}",
            {}, "{}", "{}", "{}", "{}",
            {}, "{}", TO_DATE("{}", "%Y-%m-%d")
        )
    '''.format(
        cid, fname, aname, lname, suffix, prefix, email, maidenname, degree,
        class_year, business_name, major1, major2, major3,
        masters_grad_year, job_title, NOW
    )
    do_sql(alumni_sql, INFORMIX_DEBUG)
    return alumni_sql


def set_address(request, place):

    user = request.user
    prefix = 'home'
    if place == 'WORK':
        prefix = 'business'

    address, created = Address.objects.get_or_create(
        user = user, aa = place
    )

    for f in address._meta.get_fields():
        field = f.name
        if field not in EXCLUDE_FIELDS:
            setattr(
                address, field, request.POST.get('{}_{}'.format(prefix, field))
            )

    address.updated_by = user
    address.save()


def insert_address(
    aa_type, cid, address_line1, address_line2,
    address_line3, city, state, postalcode, country, phone
):
    clear_sql = '''
        UPDATE
            stg_aludir_address
        SET
            approved = "N"
        WHERE
            id = {}
        AND
            aa = "{}"
        AND
            NVL(approved,"") = ""
    '''.format(cid, aa_type)
    do_sql(clear_sql, INFORMIX_DEBUG)
    address_sql = '''
        INSERT INTO stg_aludir_address (
            aa, id, address_line1, address_line2, address_line3, city,
            state, zip, country, phone, submitted_on
        )
        VALUES (
            "{}", {}, "{}", "{}", "{}", "{}",
            "{}", "{}", "{}", "{}", TO_DATE("{}", "%Y-%m-%d")
        )
    '''.format(
        aa_type, cid, address_line1, address_line2, address_line3,
        city, state, postalcode, country, phone, NOW
    )
    do_sql(address_sql, INFORMIX_DEBUG)
    return address_sql


def clear_activity(cid):

    clear_sql = '''
        UPDATE
            stg_aludir_activity
        SET
            approved = "N"
        WHERE
            id = {}
        AND
            NVL(approved,"") = ""
    '''.format(cid)
    do_sql(clear_sql, INFORMIX_DEBUG)


def insert_activity(cid, activityText):
    activity_sql = '''
        INSERT INTO stg_aludir_activity (
            id, activityText, submitted_on
        )
        VALUES (
            {}, "{}", TO_DATE("{}", "%Y-%m-%d")
        )
    '''.format(
        cid, activityText.strip(), NOW
    )
    do_sql(activity_sql)
    return activity_sql


def clear_privacy(cid):
    privacy_sql = 'DELETE FROM stg_aludir_privacy WHERE id = {}'.format(
        cid
    )
    do_sql(privacy_sql, INFORMIX_DEBUG)
    return privacy_sql


def privacy_manager(user, field, display):

    p, created = Privacy.objects.get_or_create(
        user = cid, updated_by = cid, fieldname = field, display = display
    )

    return created


def insert_privacy(cid, field, display):
    privacy_sql = '''
        INSERT INTO stg_aludir_privacy (
            id, fieldname, display, lastupdated
        )
        VALUES (
            {}, "{}", "{}", TO_DATE("{}", "%Y-%m-%d")
        )
        '''.format(
            cid, field, display, NOW
        )
    do_sql(privacy_sql, INFORMIX_DEBUG)
    return privacy_sql


def email_differences(cid, request):
    """
    Retrieve the existing information about the alumna
    """

    student = get_alumna(cid)

    data = {
        'cid':cid,'personal':False,'academics':False,
        'business':False,'home':False
    }

    if student['first_name']:
        first_name = student['first_name']
    else:
        first_name = '[missing first name]'

    subject = u"Alumni Directory Update for {} {} ({})".format(
        first_name, student['last_name'], cid
    )

    #
    # begin data aquisition
    #

    # needed to translate 4 letter code to major name
    majors = get_majors()

    # Obtain the most recent unapproved information about the person
    alumna = Alumna.objects.get(pk=cid)

    # Section for relatives

    # Get information about the alum's relatives
    relative_orig = get_relative(cid)
    relative_temp = Relative.objects.filter(user__id=cid)

    orig = set()
    temp = set()
    for r in relative_orig:
        # still not certain why we append '1' to primary relationships in
        # RELATIVES_ORIG sql so we strip it from here for now
        orig.add((r.lastname, r.firstname, r.relcode[:-1]))
    for r in relative_temp:
        temp.add((r.last_name, r.first_name, r.relation_code))

    relatives = orig.symmetric_difference(temp)

    data['relatives'] = relatives

    # activities/athletics information

    activities = get_activity(cid, False)
    athletics = get_activity(cid, True)

    activities_orig = []

    for a in activities:
        activities_orig.append(a)

    for a in athletics:
        activities_orig.append(a)

    activities = Activity.objects.filter(user__id=cid)

    activities_temp = []

    for a in activities:
        activities_temp.append((a.text,))

    activities_diff = []
    for temp in activities_temp:
        if temp not in activities_orig:
            activities_diff.append(temp)

    # Get address information (work and home)
    addresses = Address.objects.filter(user__id=cid)

    #
    # begin comparisions
    #

    # Section for personal information
    if(student['prefix'].lower() != alumna.prefix.lower()):
        data['prefix'] = alumna.prefix
        data['original_prefix'] = student['prefix']
        data['personal'] = True
    if(first_name != alumna.first_name):
        data['first_name'] = alumna.first_name
        data['original_first_name'] = first_name
        data['personal'] = True
    if(student['alt_name'] != alumna.alt_name):
        data['alt_name'] = alumna.alt_name
        data['original_alt_name'] = student['alt_name']
        data['personal'] = True
    if(student['birth_last_name'] != alumna.maiden_name):
        data['maiden_name'] = alumna.maiden_name
        data['original_maiden_name'] = student['birth_last_name']
        data['personal'] = True
    if(student['last_name'] != alumna.last_name):
        data['last_name'] = alumna.last_name
        data['original_last_name'] = student['last_name']
        data['personal'] = True
    if(student['suffix'].lower() != alumna.suffix.lower()):
        data['suffix'] = alumna.suffix
        data['original_suffix'] = student['suffix']
        data['personal'] = True
    if(student['email'] != alumna.email):
        data['email'] = alumna.email
        data['original_email'] = student['email']
        data['personal'] = True

    # Section for academics
    major1 = major2 = major3 = ''
    if(student['degree'] != alumna.degree):
        data['degree'] = alumna.degree
        data['original_degree'] = student['degree']
        data['academics'] = True
    for m in majors:
        if m[0] == alumna.major1:
            major1 = m[1]
            break
    if(student['major1'] != major1):
        data['major1'] = major1
        data['original_major1'] = student['major1']
        data['academics'] = True
    for m in majors:
        if m[0] == alumna.major2:
            major2 = m[1]
            break
    if(student['major2'] != major2):
        data['major2'] = major2
        data['original_major2'] = student['major2']
        data['academics'] = True
    for m in majors:
        if m[0] == alumna.major3:
            major3 = m[1]
            break
    if(student['major3'] != major3):
        data['major3'] = major3
        data['original_major3'] = student['major3']
        data['academics'] = True
    if(student['masters_grad_year'] != alumna.masters_grad_year):
        data['masters_grad_year'] = alumna.masters_grad_year
        data['original_masters_grad_year'] = student['masters_grad_year']
        data['academics'] = True

    # Section for activities
    data['organizations'] = activities_diff

    # Section for addresses
    if (len(addresses) > 0):
        for a in addresses:

            prefix = 'home'
            if a.aa == 'WORK':
                prefix = 'business'

            for f in Address._meta.get_fields():
                field = f.name
                if field not in EXCLUDE_FIELDS:
                    key = '{}_{}'.format(prefix, field)
                    val = getattr(a, field)
                    if student[key] != val:
                        data[key] = val
                        orig_key = 'original_{}'.format(key)
                        data[orig_key] = student[key]
                        data[prefix] = True

    response = None
    if settings.DEBUG:
        response = render(request, 'manager/email.html', {'data':data})
    else:
        send_mail(
            request, settings.MANAGER_RECIPIENTS, subject,
            settings.DEFAULT_FROM_EMAIL,
            'manager/email.html', data, [settings.MANAGERS[0][1],]
        )

    return response
