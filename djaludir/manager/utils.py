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
    alumna, created = Alumna.objects.get_or_create(user = user)

    for f in alumna._meta.get_fields():
        field = f.name
        if field not in EXCLUDE_FIELDS:
            setattr(alumna, field, request.POST.get(field))

    alumna.updated_by=(user)
    alumna.save()

    return alumna


def get_activities(cid, is_sports=False):
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


def set_activities(request, activity):

    user = request.user
    activities = []
    count = '{}Count'.format(activity)
    for i in range (1, int(request.POST.get(count)) + 1):
        activityText = request.POST.get('{}{}'.format(activity, str(i)))
        if activityText:
            a, created = Activity.objects.get_or_create(
                user = user, updated_by = user, text = activityText
            )
            activities.append(a)

    return activities


def get_relatives(cid):
    """
    Retrieve collection of relatives (regardless of whether the alumn(a|us)
    is the primary or secondary relationship)
    """

    relatives_sql = RELATIVES_ORIG(cid = cid)

    objs = do_sql(relatives_sql, INFORMIX_DEBUG)

    return objs.fetchall()


def set_relatives(request):

    user = request.user
    relatives = []
    for i in range (1, int(request.POST.get('relativeCount')) + 1):
        relFname = request.POST.get('relativeFname' + str(i))
        relLname = request.POST.get('relativeLname' + str(i))
        relRelation = request.POST.get('relativeText' + str(i))

        # Because of the way relationships are stored in CX,
        # we must identify if the alumn(a|us) matches the first or
        # second role in the relationship
        alumPrimary = True
        if(relRelation[-1:] == '1'):
            alumPrimary = False

        if(relRelation[-1:] == '1' or relRelation[-1:] == '2'):
            relRelation = relRelation[0:-1]

        # If the relative has some value in their name and
        # a specified relationship, insert the record
        if (len(relFname + relLname) > 0 and relRelation != ''):
            r, created = Relative.objects.get_or_create(
                user = user, updated_by = user,
                relation_code = relRelation,
                first_name = relFname, last_name = relLname,
                primary = alumPrimary
            )
            relatives.append(r)

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
        maidenname = maidenname.replace("(","").replace(")","")

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

    a, created = Address.objects.get_or_create(
        user = user, updated_by = user, aa = place,
        address_line1 = request.POST.get('{}_address'.format(prefix)),
        address_line2 = request.POST.get('{}_address2'.format(prefix)),
        address_line3 = request.POST.get('{}_address3'.format(prefix)),
        city = request.POST.get('{}_city'.format(prefix)),
        state = request.POST.get('{}_state'.format(prefix)),
        postal_code = request.POST.get('{}_zip'.format(prefix)),
        country = request.POST.get('{}_country'.format(prefix)),
        phone = request.POST.get('{}_phone'.format(prefix))
    )

    return a


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
    Retrieve the existing information about the alumn(a|us)
    """

    student = get_alumna(cid)

    data = {
        'cid':cid,'personal':False,'academics':False,
        'business':False,'home':False
    }

    if student['fname']:
        fname = student['fname']
    else:
        fname = '[missing first name]'

    subject = u"Alumni Directory Update for {} {} ({})".format(
        fname, student['lname'], cid
    )

    # Obtain the most recent unapproved information about the person
    alumna_temp = ALUMNA_TEMP(cid = cid)

    alum = do_sql(alumna_temp, INFORMIX_DEBUG)
    alumni = alum.fetchone()

    # Section for relatives

    # Get information about the alum's relatives
    relatives_orig = get_relatives(cid)
    relatives_sql = RELATIVES_TEMP(cid = cid)
    relatives_new = do_sql(relatives_sql, INFORMIX_DEBUG).fetchall()
    relatives = []
    # compare current relatives with data from POST to determine if there
    # were any changes or not
    for r1 in relatives_orig:
        ro = list(r1)
        del ro[3]
        for r2 in relatives_new:
            rn = list(r2)
            if ro != rn:
                relatives.append(rn)

    data['relatives'] = relatives
    # Loop through all the relatives' records and set approved = "N"
    clear_relative(cid)

    # activities/athletics information
    activities = get_activities(cid, False)
    athletics = get_activities(cid, True)
    activities_orig = []

    for a in activities:
        activities_orig.append(a)

    for a in athletics:
        activities_orig.append(a)

    activities_temp = do_sql(
        ACTIVITIES_TEMP(cid = cid), INFORMIX_DEBUG
    ).fetchall()
    activities_diff = []

    for temp in activities_temp:
        if temp not in activities_orig:
            activities_diff.append(temp)

    clear_activity(cid)

    # Get address information (work and home)
    home_address = do_sql(
        HOMEADDRESS_TEMP(cid = cid), INFORMIX_DEBUG
    ).fetchone()

    workaddress_sql = WORKADDRESS_TEMP(cid = cid)
    workaddress = do_sql(workaddress_sql, INFORMIX_DEBUG)
    if(workaddress != None):
        work_address = workaddress.fetchone()
    else:
        work_address = []

    # Section for personal information
    if(student['prefix'].lower() != alumni.prefix.lower()):
        data["prefix"] = alumni.prefix
        data["original_prefix"] = student['prefix']
        data["personal"] = True
    if(fname != alumni.fname):
        data["fname"] = alumni.fname
        data["original_fname"] = fname
        data["personal"] = True
    if(student['aname'] != alumni.aname):
        data["aname"] = alumni.aname
        data["original_aname"] = student['aname']
        data["personal"] = True
    if(student['birth_lname'] != alumni.maidenname):
        data["maidenname"] = alumni.maidenname
        data["original_maidenname"] = student['birth_lname']
        data["personal"] = True
    if(student['lname'] != alumni.lname):
        data["lname"] = alumni.lname
        data["original_lname"] = student['lname']
        data["personal"] = True
    if(student['suffix'].lower() != alumni.suffix.lower()):
        data["suffix"] = alumni.suffix
        data["original_suffix"] = student['suffix']
        data["personal"] = True

    #Section for academics
    if(student['degree'] != alumni.degree):
        data["degree"] = alumni.degree
        data["original_degree"] = student['degree']
        data["academics"] = True
    if(student['major1'] != alumni.major1):
        data["major1"] = alumni.major1
        data["original_major1"] = student['major1']
        data["academics"] = True
    if(student['major2'] != alumni.major2):
        data["major2"] = alumni.major2
        data["original_major2"] = student['major2']
        data["academics"] = True
    if(student['major3'] != alumni.major3):
        data["major3"] = alumni.major3
        data["original_major3"] = student['major3']
        data["academics"] = True
    if(student['masters_grad_year'] != alumni.masters_grad_year):
        data["masters_grad_year"] = alumni.masters_grad_year
        data["original_mastersgradyear"] = student['masters_grad_year']
        data["academics"] = True

    # Section for activities
    # (this may be split out into organizations vs athletics in the future)
    data["organizations"] = activities_diff

    # Section for business name
    if(student['business_name'] != alumni.business_name):
        data["business_name"] = alumni.business_name
        data["original_businessname"] = student['business_name']
        data["business"] = True
    # Section for job title
    if(student['job_title'] != alumni.job_title):
        data["job_title"] = alumni.job_title
        data["original_jobtitle"] = student['job_title']
        data["business"] = True
    # Section for work/business address
    if (work_address != None and len(work_address) > 0):
        if(student['business_address'] != work_address.address_line1):
            data["business_address"] = work_address.address_line1
            data["original_businessaddress"] = student['business_address']
            data["business"] = True
        if(student['business_address2'] != work_address.address_line2):
            data["business_address"] = work_address.address_line2
            data["original_businessaddress2"] = student['business_address2']
            data["business"] = True
        if(student['business_city'] != work_address.city):
            data["business_city"] = work_address.city
            data["original_businesscity"] = student['business_city']
            data["business"] = True
        if(student['business_state'] != work_address.state):
            data["business_state"] = work_address.state
            data["original_businessstate"] = student['business_state']
            data["business"] = True
        if(student['business_zip'] != work_address.zip):
            data["business_zip"] = work_address.zip
            data["original_businesszip"] = student['business_zip']
            data["business"] = True
        if(student['business_country'] != work_address.country):
            data["business_country"] = work_address.country
            data["original_businesscountry"] = student['business_country']
            data["business"] = True
        if(student['business_phone'] != work_address.phone):
            data["business_phone"] = work_address.phone
            data["original_businessphone"] = student['business_phone']
            data["business"] = True
    else:
        data["business"] = True
        data["business_address"] = workaddress_sql

    # Section for home address
    if(student['email'] != alumni.email):
        data["email"] = alumni.email
        data["original_email"] = student['email']
        data["home"] = True
    if(home_address != None and len(home_address) > 0):
        if(student['home_address1']!= home_address.address_line1):
            data["home_address"] = home_address.address_line1
            data["original_homeaddress"] = student['home_address1']
            data["home"] = True
        if(student['home_address2'] != home_address.address_line2):
            data["home_address2"] = home_address.address_line2
            data["original_homeaddress2"] = student['home_address2']
            data["home"] = True
        if(student['home_address3'] != home_address.address_line3):
            data["home_address3"] = home_address.address_line3
            data["original_homeaddress3"] = student['home_address3']
            data["home"] = True
        if(student['home_city'] != home_address.city):
            data["home_city"] = home_address.city
            data["original_homecity"] = student['home_city']
            data["home"] = True
        if(student['home_state'] != home_address.state):
            data["home_state"] = home_address.state
            data["original_homestate"] = student['home_state']
            data["home"] = True
        if(student['home_zip'] != home_address.zip):
            data["home_zip"] = home_address.zip
            data["original_homezip"] = student['home_zip']
            data["home"] = True
        if(student['home_country'] != home_address.country):
            data["home_country"] = home_address.country
            data["original_homecountry"] = student['home_country']
            data["home"] = True
        if(student['home_phone'] != home_address.phone):
            data["home_phone"] = home_address.phone
            data["original_homephone"] = student['home_phone']
            data["home"] = True

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
