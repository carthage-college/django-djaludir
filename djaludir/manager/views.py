from datetime import date
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader, Context
from django.contrib.auth.decorators import login_required

from djtools.utils.mail import send_mail
from djzbar.utils.informix import do_sql

import datetime
import json

if settings.DEBUG:
    TO_LIST = ["mkishline@carthage.edu",]
else:
    TO_LIST = ["mkishline@carthage.edu",]

ATHLETIC_IDS = "'S019','S020','S021','S022','S228','S043','S044','S056','S057','S073','S079','S080','S083','S090','S095','S220','S100','S101','S109','S126','S131','S156','S161','S172','S173','S176','S186','S187','S196','S197','S204','S205','S207','S208','S253','S215','S216'"

@login_required
def display(request, student_id):
    alumni = getStudent(student_id)
    activities = getStudentActivities(student_id, False)
    athletics = getStudentActivities(student_id, True)
    relatives = getRelatives(student_id)

    return render_to_response(
        "manager/display.html",
        {'studentID':student_id, 'person':alumni, 'activities':activities, 'athletics':athletics, 'relatives':relatives},
        context_instance=RequestContext(request)
    )

@login_required
def update(request):
    studentID = request.POST.get('carthageID')

    #Insert personal information
    insertAlumni(studentID, request.POST.get('fname'), request.POST.get('lname'), request.POST.get('suffix'), request.POST.get('prefix'),
                   request.POST.get('email'), request.POST.get('maidenname'), request.POST.get('degree'), request.POST.get('class_year'), request.POST.get('business_name'),
                   request.POST.get('major1'), request.POST.get('major2'), request.POST.get('major3'), request.POST.get('masters_grad_year'), request.POST.get('job_title'))

    #Loop through all the relatives records
    for relativeIndex in range (1, int(request.POST.get('relativeCount'))):
        relFname = request.POST.get('relativeFname' + str(relativeIndex))
        relLname = request.POST.get('relativeLname' + str(relativeIndex))
        relRelation = request.POST.get('relativeText' + str(relativeIndex))
        alumPrimary = 'Y'
        if(relRelation[-1:] == '1'):
            alumPrimary = 'N'

        if(relRelation[-1:] == '1' or relRelation[-1:] == '2'):
            relRelation = relRelation[0:-1]

        if(len(relFname + relLname) > 0 and relRelation != ''):
            insertRelative(studentID, relRelation, relFname, relLname, alumPrimary)


    #Insert organizationa and athletic involvement
    for activityIndex in range (0, int(request.POST.get('activityCount'))):
        activityText = request.POST.get('activity' + str(activityIndex))

        if(len(activityText) > 0):
            insertActivity(studentID, activityText)

    for athleticIndex in range (0, int(request.POST.get('athleticCount'))):
        athleticText = request.POST.get('athletic' + str(athleticIndex))

        if(len(athleticText) > 0):
            insertActivity(studentID, athleticText)

    #Insert home and work address information
    insertAddress('WORK', studentID, request.POST.get('business_address'), '', '',
                  request.POST.get('business_city'), request.POST.get('business_state'), request.POST.get('business_zip'), '', request.POST.get('business_phone'))

    insertAddress('HOME', studentID, request.POST.get('home_address1'), request.POST.get('home_address2'), request.POST.get('home_address3'),
                  request.POST.get('home_city'), request.POST.get('home_state'), request.POST.get('home_zip'), '', request.POST.get('home_phone'))


    #Clear privacy values
    clearPrivacy(studentID)

    #Insert updated privacy settings
    personal = request.POST.get('privacyPersonal','Y')
    insertPrivacy(studentID, 'Personal', personal)

    family = request.POST.get('privacyFamily','Y')
    insertPrivacy(studentID, 'Family', family)

    academics = request.POST.get('privacyAcademics','Y')
    insertPrivacy(studentID, 'Academics', academics)

    professional = request.POST.get('privacyProfessional','Y')
    insertPrivacy(studentID, 'Professional', professional)

    address = request.POST.get('privacyAddress','Y')
    insertPrivacy(studentID, 'Address', address)

    return HttpResponseRedirect(reverse('manager_user_edit_success', kwargs={'student_id':studentID}))

@login_required
def search(request):
    fieldlist = []
    terms = []
    matches = []
    sql = ''
    if request.method == 'POST':
        orSQL = ''
        andSQL = ''
        #Sport/activities are searched via "OR", all other fields are "AND" so assemble the list of fields to run through the logic to create the appropriate filters
        for rowNum in range (0, int(request.POST.get('maxCriteria')) + 1):
            fieldname = request.POST.get('within' + str(rowNum))
            searchterm = request.POST.get('term' + str(rowNum))

            if fieldname is not None and searchterm is not None and searchterm != '':
                fieldlist += (fieldname,)
                terms += (searchterm,)

                if fieldname == 'activity':
                    if len(orSQL) > 0:
                        orSQL += 'OR '
                    orSQL += 'LOWER(invl_table.txt) LIKE "%%%s%%" ' % (searchterm.lower())
                else:
                    if len(andSQL) > 0:
                        andSQL += 'AND '
                    andSQL += 'LOWER(TRIM(%s::varchar(250))) LIKE "%%%s%%" ' % (fieldname, searchterm.lower())

        #Based on the criteria specified by the user, add the necessary tables to the search query
        selectFromSQL = ('SELECT DISTINCT alum.cl_yr AS class_year, ids.firstname, maiden.lastname AS maiden_name, ids.lastname, ids.id, LOWER(ids.lastname) AS sort1, LOWER(ids.firstname) AS sort2 '
                     'FROM alum_rec alum INNER JOIN id_rec ids ON alum.id = ids.id '
                     ' LEFT JOIN (SELECT prim_id, MAX(active_date) active_date FROM addree_rec WHERE style = "M" GROUP BY prim_id) prevmap ON ids.id = prevmap.prim_id'
                     ' LEFT JOIN addree_rec maiden ON maiden.prim_id = prevmap.prim_id AND maiden.active_date = prevmap.active_date AND maiden.style = "M"')
        #If search criteria includes activity or sport add the involvement tables
        if 'activity' in fieldlist:
            selectFromSQL += (
                     'LEFT JOIN involve_rec ON ids.id = involve_rec.id '
                     'LEFT JOIN invl_table ON involve_rec.invl = invl_table.invl ')

        #If search criteria includes the student's major
        #QUESTION - Should we check all three major fields for each major specified or is sequence important?
        if 'major1.txt' in fieldlist or 'major2.txt' in fieldlist:
            selectFromSQL += (' LEFT JOIN prog_enr_rec progs ON ids.id = progs.id AND progs.acst = "GRAD"')
            if 'major1.txt' in fieldlist:
                selectFromSQL += (' LEFT JOIN major_table major1 ON progs.major1 = major1.major')
            if 'major2.txt' in fieldlist:
                selectFromSQL += (' LEFT JOIN major_table major2 ON progs.major2 = major2.major')

        #If search criteria were submitted, flesh out the sql query. Include "and's", "or's" and sorting
        if len(andSQL + orSQL) > 0:
            if len(orSQL) > 0:
                orSQL = '(%s)' % (orSQL)
            if len(andSQL) > 0 and len(orSQL) > 0:
                andSQL = 'AND %s' % (andSQL)
            sql = '%s WHERE %s %s ORDER BY LOWER(ids.lastname), LOWER(ids.firstname), alum.cl_yr' % (selectFromSQL, orSQL, andSQL)

            matches = do_sql(sql, key="debug")
            matches = matches.fetchall()

    return render_to_response(
        "manager/search.html",
        {'searching':dict(zip(fieldlist, terms)), 'matches':matches, 'debug':sql},
        context_instance=RequestContext(request)
    )

@login_required
def edit(request, student_id, success=False):
    #Retrieve relevant information about the alumni
    alumni = getStudent(student_id)
    activities = getStudentActivities(student_id, False)
    athletics = getStudentActivities(student_id, True)
    relatives = getRelatives(student_id)
    privacy = getPrivacy(student_id)

    #Assemble collections for the user to make choices
    majors = getMajors()
    prefixes = dict([('',''),('DR','Dr'),('MR','Mr'),('MRS','Mrs'),('MS','Ms'),('REV','Rev')])
    suffixes = ('','II','III','IV','JR','MD','PHD','SR')
    year_range = range(1900, date.today().year + 1)
    relationships = getRelationships()
    countries = getCountries()

    return render_to_response(
        "manager/edit.html",
        {'submitted':success,'studentID':student_id, 'person':alumni, 'activities':activities, 'athletics':athletics,
         'relatives':relatives, 'privacy':privacy, 'majors':majors, 'prefixes':prefixes, 'suffixes':suffixes,
         'years':year_range, 'relationships':relationships, 'countries':countries},
        context_instance=RequestContext(request)
    )

def getStudent(student_id):
    sql = ('SELECT DISTINCT'
           '    ids.id AS carthage_id, TRIM(ids.firstname) AS fname, TRIM(ids.lastname) AS lname, TRIM(ids.suffix) AS suffix, TRIM(INITCAP(ids.title)) AS prefix, TRIM(email.line1) email,'
           '    CASE'
           '        WHEN    NVL(ids.decsd, "N")    =    "Y"                THEN    1'
           '                                                               ELSE    0'
           '    END    AS is_deceased,'
           '    TRIM(maiden.lastname) AS birth_lname, TRIM(progs.deg) AS degree,'
           '    CASE'
           '        WHEN    TRIM(progs.deg)    IN    ("BA","BS")           THEN    alum.cl_yr'
           '                                                               ELSE    0'
           '    END    AS    class_year, TRIM(aawork.line1) AS business_name, TRIM(aawork.line2) AS business_address, TRIM(aawork.city) AS business_city, TRIM(aawork.st) AS business_state,'
           '    TRIM(aawork.zip) AS business_zip, TRIM(aawork.ctry) AS business_country, TRIM(aawork.phone) AS business_phone, TRIM(ids.addr_line1) AS home_address1,'
           '    TRIM(ids.addr_line2) AS home_address2, TRIM(ids.addr_line3) AS home_address3, TRIM(ids.city) AS home_city, TRIM(ids.st) AS home_state,'
           '    TRIM(ids.zip) AS home_zip, TRIM(ids.ctry) AS home_country, TRIM(ids.phone) AS home_phone,'
           '    TRIM('
           '        CASE'
           '              WHEN    TRIM(progs.deg) IN    ("BA","BS")        THEN    major1.txt'
           '                                                               ELSE    conc1.txt'
           '       END'
           '    )    AS    major1,'
           '    TRIM('
           '        CASE'
           '               WHEN    TRIM(progs.deg)    IN    ("BA","BS")    THEN    major2.txt'
           '                                                               ELSE    conc2.txt'
           '        END'
           '    )    AS    major2,'
           '    TRIM('
           '        CASE'
           '               WHEN    TRIM(progs.deg)    IN    ("BA","BS")    THEN    major3.txt'
           '                                                               ELSE    ""'
           '        END'
           '    )    AS    major3,'
           '    CASE'
           '        WHEN    TRIM(progs.deg)    NOT IN ("BA","BS")          THEN    alum.cl_yr'
           '                                                               ELSE    0'
           '    END    AS    masters_grad_year'
           ' FROM    alum_rec    alum   INNER JOIN    id_rec            ids     ON    alum.id                =        ids.id'
           '                            LEFT JOIN    ('
           '                                SELECT prim_id, MAX(active_date) active_date'
           '                                FROM addree_rec'
           '                                WHERE style = "M"'
           '                                GROUP BY prim_id'
           '                            )                            prevmap    ON    ids.id                =       prevmap.prim_id'
           '                            LEFT JOIN    addree_rec      maiden     ON    maiden.prim_id        =       prevmap.prim_id'
           '                                                                    AND   maiden.active_date    =       prevmap.active_date'
           '                                                                    AND   maiden.style          =       "M"'
           '                            LEFT JOIN    aa_rec          email      ON    ids.id                =       email.id'
           '                                                                    AND   email.aa              =       "EML2"'
           '                                                                    AND   TODAY                 BETWEEN email.beg_date    AND    NVL(email.end_date, TODAY)'
           '                            LEFT JOIN    aa_rec          aawork     ON    ids.id                =       aawork.id'
           '                                                                    AND   aawork.aa             =       "WORK"'
           '                                                                    AND   TODAY                 BETWEEN aawork.beg_date   AND    NVL(aawork.end_date, TODAY)'
           '                            LEFT JOIN    prog_enr_rec    progs      ON    ids.id                =       progs.id'
           '                                                                    AND   progs.acst            =       "GRAD"'
           '                            LEFT JOIN    major_table     major1     ON    progs.major1          =       major1.major'
           '                            LEFT JOIN    major_table     major2     ON    progs.major2          =       major2.major'
           '                            LEFT JOIN    major_table     major3     ON    progs.major3          =       major3.major'
           '                            LEFT JOIN    conc_table      conc1      ON    progs.conc1           =       conc1.conc'
           '                            LEFT JOIN    conc_table      conc2      ON    progs.conc2           =       conc2.conc'
           ' WHERE   NVL(ids.decsd, "N") =   "N"'
           ' AND     ids.id              =   %s' %   (student_id)
    )
    student = do_sql(sql)
    return student.fetchone()

def getStudentActivities(student_id, isSports = False):
    fieldname = 'activity' if not isSports else 'sport'
    comparison = 'NOT' if not isSports else ''

    activities_sql = (
        'SELECT TRIM(invl_table.txt)    AS  %s'
        ' FROM   invl_table  INNER JOIN  involve_rec ON  invl_table.invl =   involve_rec.invl'
        ' WHERE  involve_rec.id  =       %s'
        ' AND    invl_table.invl MATCHES "S[0-9][0-9][0-9]"'
        ' AND    invl_table.invl %s IN  (%s)'
        ' ORDER BY   TRIM(invl_table.txt)'   %   (fieldname, student_id, comparison, ATHLETIC_IDS)
    )
    activities = do_sql(activities_sql)
    return activities.fetchall()

def getRelatives(student_id):
    relatives_sql = (' SELECT'
                     '    TRIM('
                     '      CASE'
                     '            WHEN    rel.prim_id    =    %s    THEN    sec.firstname'
                     '                                              ELSE    prim.firstname'
                     '      END'
                     '    )    AS    firstName,'
                     '    TRIM('
                     '        CASE'
                     '            WHEN    rel.prim_id    =    %s    THEN    sec.lastname'
                     '                                              ELSE    prim.lastname'
                     '        END'
                     '    )    AS    lastName,'
                     '    TRIM('
                     '        CASE'
                     '            WHEN    rel.prim_id    =    %s    THEN    reltbl.sec_txt'
                     '                                              ELSE    reltbl.prim_txt'
                     '        END'
                     '    )    AS    relText,'
                     '    TRIM(reltbl.rel) ||'
                     '    CASE'
                     '        WHEN    rel.prim_id   =   %s  THEN    "2"'
                     '                                      ELSE    "1"'
                     '    END AS relCode'
                     ' FROM    relation_rec    rel    INNER JOIN    id_rec      prim    ON    rel.prim_id   =    prim.id'
                     '                                INNER JOIN    id_rec      sec     ON    rel.sec_id    =    sec.id'
                     '                                INNER JOIN    rel_table   reltbl  ON    rel.rel       =    reltbl.rel'
                     ' WHERE prim_id =   %s'
                     ' OR    sec_id  =   %s' % (student_id, student_id, student_id, student_id, student_id, student_id)
    )
    relatives = do_sql(relatives_sql)
    return relatives.fetchall()

def getPrivacy(student_id):
    privacy_sql = ("SELECT TRIM(fieldname) AS fieldname, TRIM(display) AS display FROM stg_aludir_privacy WHERE id = %s") % (student_id)
    privacy = do_sql(privacy_sql)
    return privacy.fetchall()

def getRelationships():
    #relationship_sql = 'SELECT TRIM(rel_table.rel) AS rel, TRIM(rel_table.txt) AS txt FROM rel_table WHERE rel IN ("AUNN","COCO","GPGC","HW","PC","SBSB")'
    #relationships = do_sql(relationship_sql)
    #return relationships.fetchall()
    relationships = dict([('',''),('HW1','Husband'),('HW2','Wife'),('PC1','Parent'),('PC2','Child'),('SBSB','Sibling'),('COCO','Cousin'),('GPGC1','Grandparent'),('GPGC2','Grandchild'),('AUNN1','Aunt/Uncle'),('AUNN2','Niece/Nephew')])
    return relationships

def getMajors():
    major_sql = 'SELECT DISTINCT TRIM(major) AS major_code, TRIM(txt) AS major_name FROM major_table ORDER BY TRIM(txt)'
    majors = do_sql(major_sql)
    return majors.fetchall()

def getCountries():
    countries_sql = 'SELECT TRIM(ctry) AS ctry, TRIM(txt) AS txt FROM ctry_table ORDER BY web_ord, TRIM(txt)'
    countries = do_sql(countries_sql)
    return countries.fetchall()

def search_activity(request):
    search_string = request.GET.get("term","Football")
    activity_search_sql = 'SELECT TRIM(invl_table.txt) txt FROM invl_table WHERE invl_table.invl MATCHES "S[0-9][0-9][0-9]" AND LOWER(invl_table.txt) LIKE "%%%s%%" ORDER BY TRIM(invl_table.txt)' % (search_string.lower())
    activity_search = do_sql(activity_search_sql)
    #return activity_search.fetchall()
    #context = json.dumps(activity_search.fetchall())
    return HttpResponse(activity_search.fetchall())

def insertRelative(carthageID, relCode, fname, lname, alumPrimary):
    relation_sql = "INSERT INTO stg_aludir_relative (id, relationCode, fname, lname, alum_primary, submitted_on) VALUES (%s, '%s', '%s', '%s', '%s', '%s')" % (carthageID, relCode, fname, lname, alumPrimary, datetime.datetime.now())
    do_sql(relation_sql)
    return relation_sql

def insertAlumni(carthageID, fname, lname, suffix, prefix, email, maidenname, degree, class_year, business_name, major1, major2, major3, masters_grad_year, job_title):
    alumni_sql = ('INSERT INTO stg_aludir_alumni (id, fname, lname, suffix, prefix, email, maidenname, degree, class_year, business_name, major1, major2, major3, masters_grad_year, '
                  'job_title, submitted_on)'
                  'VALUES (%s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s,  "%s", "%s", "%s", "%s", %s, "%s", "%s")'
                  % (carthageID, fname, lname, suffix, prefix, email, maidenname, degree, class_year, business_name, major1, major2, major3, masters_grad_year, job_title, datetime.datetime.now())
    )
    do_sql(alumni_sql)
    return alumni_sql

def insertAddress(aa_type, carthageID, address_line1, address_line2, address_line3, city, state, postalcode, country, phone):
    address_sql = ('INSERT INTO stg_aludir_address (aa, id, address_line1, address_line2, address_line3, city, state, zip, country, phone, submitted_on)'
                   'VALUES ("%s", %s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")'
                   % (aa_type, carthageID, address_line1, address_line2, address_line3, city, state, postalcode, country, phone, datetime.datetime.now())
    )
    do_sql(address_sql)
    return address_sql

def insertActivity(carthageID, activityText):
    activity_sql = 'INSERT INTO stg_aludir_activity (id, activityText) VALUES (%s, "%s", "%s")' % (carthageID, activityText, datetime.datetime.now())
    do_sql(activity_sql)
    return activity_sql

def clearPrivacy(carthageID):
    privacy_sql = 'DELETE FROM stg_aludir_privacy WHERE id = %s' % (carthageID)
    do_sql(privacy_sql)
    return privacy_sql

def insertPrivacy(carthageID, field, display):
    privacy_sql = 'INSERT INTO stg_aludir_privacy (id, fieldname, display, lastupdated) VALUES (%s, "%s", "%s", "%s")' % (carthageID, field, display, datetime.datetime.now())
    do_sql(privacy_sql)
    return privacy_sql

def emailDifferences(studentID):
    emailBody = ''
    student = getStudent(studentID)

    #Get information about the person
    alumni_sql = ("SELECT FIRST 1 TRIM(fname) AS fname, TRIM(lname) AS lname, TRIM(suffix) AS suffix, TRIM(prefix) AS prefix, TRIM(email) AS email, TRIM(maidenname) AS maidenname,"
                  "TRIM(degree) AS degree, class_year, TRIM(business_name) AS business_name, TRIM(major1) AS major1, TRIM(major2) AS major2, TRIM(major3) AS major3, masters_grad_year,"
                  "TRIM(job_title) AS job_title FROM stg_aludir_alumni WHERE id = %s ORDER BY alum_no DESC") % (studentID)
    alum = do_sql(alumni_sql)
    alumni = alum.fetchone()

    #Get information about the alum's relatives
    relatives_sql = ("SELECT TRIM(fname) AS fname, TRIM(lname) AS lname, TRIM(relcode) AS relcode FROM stg_aludir_relative WHERE id = %s AND approved = ''") % (studentID)
    relatives = do_sql(relatives_sql).fetchall()

    #Get address information (work and home)
    homeaddress_sql = ("SELECT FIRST 1 TRIM(address_line1) AS address_line1, TRIM(address_line2) AS address_line2, TRIM(address_line3) AS address_line3, TRIM(city) AS city, TRIM(state) AS state,"
                       "TRIM(zip) AS zip, TRIM(country) AS country, TRIM(phone) AS phone WHERE id = %s AND aa_type = '%s' ORDER BY aa_no DESC") % (studentID, 'HOME')
    homeaddress = do_sql(homeaddress_sql)
    home_address = homeaddress.fetchone()

    workaddress_sql = ("SELECT FIRST 1 TRIM(address_line1) AS address_line1, TRIM(address_line2) AS address_line2, TRIM(address_line3) AS address_line3, TRIM(city) AS city, TRIM(state) AS state,"
                       "TRIM(zip) AS zip, TRIM(country) AS country, TRIM(phone) AS phone WHERE id = %s AND aa_type = '%s' ORDER BY aa_no DESC") % (studentID, 'WORK')
    workaddress = do_sql(workaddress_sql)
    work_address = workaddress.fetchone()

    #Get organization information
    activities_sql = ("SELECT activityText FROM stg_aludir_activity WHERE id = %s AND approved = ''") % (studentID)
    alum_activities = do_sql(activities_sql)

    data = []
    #Section for personal information
    if(student.prefix != alumni.prefix):
        data["prefix"] = alumni.prefix
        data["original_prefix"] = student.prefix
    if(student.fname != alumni.fname):
        data["fname"] = alumni.fname
        data["original_fname"] = student.fname
    if(student.birth_lname != alumni.maidenname):
        data["maidenname"] = alumni.maidenname
        data["original_maidenname"] = student.birth_lname
    if(student.lname != alumni.lname):
        data["lname"] = alumni.lname
        data["original_lname"] = student.lname
    if(student.suffix != alumni.suffix):
        data["suffix"] = alumni.suffix
        data["original_suffix"] = student.suffix

    #Section for relatives
    if(len(relatives) > 0):
        data["relatives"] = relatives

    #Section for academics
    if(student.degree != alumni.degree):
        data["degree"] = alumni.degree
        data["original_degree"] = student.degree
    if(student.major1 != alumni.major1):
        data["major1"] = alumni.major1
        data["original_major1"] = student.major1
    if(student.major2 != alumni.major2):
        data["major2"] = alumni.major2
        data["original_major2"] = student.major2
    if(student.major3 != alumni.major3):
        data["major3"] = alumni.major3
        data["original_major3"] = student.major3
    if(student.masters_grad_year != alumni.masters_grad_year):
        data["masters_grad_year"] = alumni.masters_grad_year
        data["original_mastersgradyear"] = student.masters_grad_year

    #Section for activities (this may get split out into organizations vs athletics in the future)
    if(len(alum_activities) > 0):
        data["organizations"] = alum_activities

    if(student.business_name != alumni.business_name):
        data["business_name"] = alumni.business_name
        data["original_businessname"] = student.business_name
    if(student.job_title != alumni.job_title):
        data["job_title"] = alumni.job_title
        data["original_jobtitle"] = student.job_title

    #Section for work address
    if(student.business_address != work_address.address_line1):
        data["business_address"] = work_address.address_line1
        data["original_businessaddress"] = student.business_address
    if(student.business_city != work_address.city):
        data["business_city"] = work_address.city
        data["original_businesscity"] = student.business_city
    if(student.business_state != work_address.state):
        data["business_state"] = work_address.state
        data["original_businessstate"] = student.business_state
    if(student.business_zip != work_address.zip):
        data["business_zip"] = work_address.zip
        data["original_businesszip"] = student.business_zip
    if(student.business_country != work_address.country):
        data["business_country"] = work_address.country
        data["original_businesscountry"] = student.business_country
    if(student.business_phone != work_address.phone):
        data["business_phone"] = work_address.phone
        data["original_businessphone"] = student.business_phone

    #Section for home address
    if(student.home_address != home_address.address_line1):
        data["home_address"] = home_address.address_line1
        data["original_homeaddress"] = student.home_address1
    if(student.home_address2 != home_address.address_line2):
        data["home_address2"] = home_address.address_line2
        data["original_homeaddress2"] = student.home_address2
    if(student.home_address3 != home_address.address_line3):
        data["home_address3"] = home_address.address_line3
        data["original_homeaddress3"] = student.home_address3
    if(student.home_city != home_address.city):
        data["home_city"] = home_address.city
        data["original_homecity"] = student.home_city
    if(student.home_state != home_address.state):
        data["home_state"] = home_address.state
        data["original_homestate"] = student.home_state
    if(student.home_zip != home_address.zip):
        data["home_zip"] = home_address.zip
        data["original_homezip"] = student.home_zip
    if(student.home_country != home_address.country):
        data["home_country"] = home_address.country
        data["original_homecountry"] = student.home_country
    if(student.home_phone != home_address.phone):
        data["home_phone"] = home_address.phone
        data["original_homephone"] = student.home_phone
    
    send_mail(
        None, 'Alumni Directory Update', 'mkishline@carthage.edu',
        'manager/email.html', data
    )
    
    """
    #Section for personal information
    if(student.prefix != alumni.prefix):
        emailBody += ('Prefix: changed from "%s" to "%s"<br />') % (student.prefix, alumni.prefix)
    if(student.fname != alumni.fname):
        emailBody += ('First Name: changed from "%s" to "%s"<br />') % (student.fname, alumni.fname)
    if(student.birth_lname != alumni.maidenname):
        emailBody += ('Maiden Name: changed from "%s" to "%s"<br />') % (student.birth_lname, alumni.maidenname)
    if(student.lname != alumni.lname):
        emailBody += ('Last Name: changed from "%s" to "%s"<br />') % (student.lname, alumni.lname)
    if(student.suffix != alumni.suffix):
        emailBody += ('Suffix: changed from "%s" to "%s"<br />') % (student.suffix, alumni.suffix)

    #Section for relatives
    if(len(relatives) > 0):
        emailBody += 'Relatives: '
        for rel in relatives :
            emailBody += ('"%s" "%s" ("%s")<br />') % (rel.fname, rel.lname, rel.relcode)
        emailBody += '<br />'

    #Section for academics
    if(student.degree != alumni.degree):
        emailBody += ('Degree: changed from "%s" to "%s"<br />') % (student.degree, alumni.degree)
    if(student.major1 != alumni.major1):
        emailBody += ('Major 1: changed from "%s" to "%s"<br />') % (student.major1, alumni.major1)
    if(student.major2 != alumni.major2):
        emailBody += ('Major 2: changed from "%s" to "%s"<br />') % (student.major2, alumni.major2)
    if(student.major3 != alumni.major3):
        emailBody += ('Major 3: changed from "%s" to "%s"<br />') % (student.major3, alumni.major3)
    if(student.masters_grad_year != alumni.masters_grad_year):
        emailBody += ('Masters Grad Year: changed from "%s" to "%s"<br />') % (student.masters_grad_year, alumni.masters_grad_year)

    #Section for activities (this may get split out into organizations vs athletics in the future)
    if(len(alum_activities) > 0):
        emailBody += 'Organization: '
        for org in alum_activities:
            emailBody += ('"%s"<br />') % (org.activityText)
        emailBody += '<br />'

    if(student.business_name != alumni.business_name):
        emailBody += ('Business Name: changed from "%s" to "%s"<br />') % (student.business_name, alumni.business_name)
    if(student.job_title != alumni.job_title):
        emailBody += ('Job Title: changed from "%s" to "%s"<br />') % (student.job_title, alumni.job_title)

    #Section for work address
    if(student.business_address != work_address.address_line1):
        emailBody += ('Business Address: changed from "%s" to "%s"<br />') % (student.business_address, work_address.address_line1)
    if(student.business_city != work_address.city):
        emailBody += ('Business City: changed from "%s" to "%s"<br />') % (student.business_city, work_address.city)
    if(student.business_state != work_address.state):
        emailBody += ('Business State: changed from "%s" to "%s"<br />') % (student.business_state, work_address.state)
    if(student.business_zip != work_address.zip):
        emailBody += ('Business Zip: changed from "%s" to "%s"<br />') % (student.business_zip, work_address.zip)
    if(student.business_country != work_address.country):
        emailBody += ('Business Country: changed from "%s" to "%s"<br />') % (student.business_country, work_address.country)
    if(student.business_phone != work_address.phone):
        emailBody += ('Business Phone: changed from "%s" to "%s"<br />') % (student.business_phone, work_address.phone)

    #Section for home address
    if(student.home_address != home_address.address_line1):
        emailBody += ('Home Address: changed from "%s" to "%s"<br />') % (student.home_address1, home_address.address_line1)
    if(student.home_address != home_address.address_line2):
        emailBody += ('Home Address Line 2: changed from "%s" to "%s"<br />') % (student.home_address2, home_address.address_line2)
    if(student.home_address != home_address.address_line3):
        emailBody += ('Home Address Line 3: changed from "%s" to "%s"<br />') % (student.home_address3, home_address.address_line3)
    if(student.home_city != home_address.city):
        emailBody += ('Home City: changed from "%s" to "%s"<br />') % (student.home_city, home_address.city)
    if(student.home_state != home_address.state):
        emailBody += ('Home State: changed from "%s" to "%s"<br />') % (student.home_state, home_address.state)
    if(student.home_zip != home_address.zip):
        emailBody += ('Home Zip: changed from "%s" to "%s"<br />') % (student.home_zip, home_address.zip)
    if(student.home_country != home_address.country):
        emailBody += ('Home Country: changed from "%s" to "%s"<br />') % (student.home_country, home_address.country)
    if(student.home_phone != home_address.phone):
        emailBody += ('Home Phone: changed from "%s" to "%s"<br />') % (student.home_phone, home_address.phone)
    """