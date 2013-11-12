from datetime import date
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader, Context

from djtools.utils.mail import send_mail
from djzbar.utils.informix import do_sql

"""
if settings.DEBUG:
    TO_LIST = ["larry@carthage.edu",]
else:
    TO_LIST = ["someone@carthage.edu",]
BCC = settings.MANAGERS

def myview(request):
    if request.method=='POST':
        form = MyForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()
            email = settings.DEFAULT_FROM_EMAIL
            if data.email:
                email = data.email
            subject = "[Submit] %s %s" % (data.first_name,data.last_name)
            send_mail(request,TO_LIST, subject, email,"myapp/email.html", data, BCC)
            return HttpResponseRedirect('/myapp/success/')
    else:
        form = MyForm()
    return render_to_response("myapp/form.html",
        {"form": form,}, context_instance=RequestContext(request))
"""

if settings.DEBUG:
    TO_LIST = ["mkishline@carthage.edu",]
else:
    TO_LIST = ["mkishline@carthage.edu",]

ATHLETIC_IDS = "'S019','S020','S021','S022','S228','S043','S044','S056','S057','S073','S079','S080','S083','S090','S095','S220','S100','S101','S109','S126','S131','S156','S161','S172','S173','S176','S186','S187','S196','S197','S204','S205','S207','S208','S253','S215','S216'"

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

def update(request):
    return render_to_response(
        "manager/update.html",
        context_instance=RequestContext(request)
    )

def search(request):
    fieldlist = []
    terms = []
    matches = []
    sql = ''
    if request.method == 'POST':
        sql = ''
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
        if 'activity' in fieldlist:
            selectFromSQL += (
                     'LEFT JOIN involve_rec ON ids.id = involve_rec.id '
                     'LEFT JOIN invl_table ON involve_rec.invl = invl_table.invl ')
        if 'major1.txt' in fieldlist or 'major2.txt' in fieldlist:
            selectFromSQL += (' LEFT JOIN prog_enr_rec progs ON ids.id = progs.id AND progs.acst = "GRAD"')
            if 'major1.txt' in fieldlist:
                selectFromSQL += (' LEFT JOIN major_table major1 ON progs.major1 = major1.major')
            if 'major2.txt' in fieldlist:
                selectFromSQL += (' LEFT JOIN major_table major2 ON progs.major2 = major2.major')


        if len(andSQL + orSQL) > 0:
            if len(orSQL) > 0:
                orSQL = '(%s)' % (orSQL)
            if len(andSQL) > 0 and len(orSQL) > 0:
                andSQL = 'AND %s' % (andSQL)
            sql = '%s WHERE %s %s ORDER BY LOWER(ids.lastname), LOWER(ids.firstname), alum.cl_yr' % (selectFromSQL, orSQL, andSQL)
            
        if len(sql) > 0:
            matches = do_sql(sql, key="debug")
            matches = matches.fetchall()
    
    return render_to_response(
        "manager/search.html",
        #{'fields':fieldlist, 'terms':terms, 'matches':matches, 'debug':sql},
        {'searching':dict(zip(fieldlist, terms)), 'matches':matches, 'debug':sql},
        context_instance=RequestContext(request)
    )

def edit(request, student_id):
    #Retrieve relevant information about the alumni
    alumni = getStudent(student_id)
    activities = getStudentActivities(student_id, False)
    athletics = getStudentActivities(student_id, True)
    relatives = getRelatives(student_id)
    
    #Assemble collections for the user to make choices
    majors = getMajors()
    prefixes = dict([('',''),('DR','Dr'),('MR','Mr'),('MRS','Mrs'),('MS','Ms'),('REV','Rev')])
    suffixes = ('','II','III','IV','JR','MD','PHD','SR')
    year_range = range(1900, date.today().year + 1)
    
    return render_to_response(
        "manager/edit.html",
        {'studentID':student_id, 'person':alumni, 'activities':activities, 'athletics':athletics, 'relatives':relatives,
         'majors':majors, 'prefixes':prefixes, 'suffixes':suffixes, 'years':year_range},
        context_instance=RequestContext(request)
    )

def getStudent(student_id):
    sql = ('SELECT DISTINCT'
           '    ids.id AS carthage_id, TRIM(ids.firstname) AS fname, TRIM(ids.lastname) AS lname, TRIM(ids.suffix) AS suffix, TRIM(INITCAP(ids.title)) AS prefix, TRIM(email.line1) email,'
           '    CASE'
           '        WHEN    NVL(ids.decsd, "N")    =    "Y"         THEN    1'
           '                                                    ELSE    0'
           '    END    AS is_deceased,'
           '    TRIM(maiden.lastname) AS birth_lname, TRIM(progs.deg) AS degree,'
           '    CASE'
           '        WHEN    TRIM(progs.deg)    IN    ("BA","BS")     THEN    alum.cl_yr'
           '                                                    ELSE    0'
           '    END    AS    class_year, TRIM(aawork.line1) AS business_name, TRIM(aawork.line2) AS business_address, TRIM(aawork.city) AS business_city, TRIM(aawork.st) AS business_state,'
           '    TRIM(aawork.zip) AS business_zip, TRIM(aawork.ctry) AS business_country, TRIM(aawork.phone) AS business_phone, TRIM(ids.addr_line1) AS home_address1,'
           '    TRIM(ids.addr_line2) AS home_address2, TRIM(ids.addr_line3) AS home_address3, TRIM(ids.city) AS home_city, TRIM(ids.st) AS home_state,'
           '    TRIM(ids.zip) AS home_zip, TRIM(ids.ctry) AS home_country, TRIM(ids.phone) AS home_phone,'
           '    TRIM('
           '        CASE'
           '              WHEN    TRIM(progs.deg) IN    ("BA","BS")    THEN    major1.txt'
           '                                                    ELSE    conc1.txt'
           '       END'
           '    )    AS    major1,'
           '    TRIM('
           '        CASE'
           '               WHEN    TRIM(progs.deg)    IN    ("BA","BS")    THEN    major2.txt'
           '                                                       ELSE    conc2.txt'
           '        END'
           '    )    AS    major2,'
           '    TRIM('
           '        CASE'
           '               WHEN    TRIM(progs.deg)    IN    ("BA","BS")    THEN    major3.txt'
           '                                                       ELSE    ""'
           '        END'
           '    )    AS    major3,'
           '    CASE'
           '        WHEN    TRIM(progs.deg)    NOT IN ("BA","BS")    THEN    alum.cl_yr'
           '                                                        ELSE    0'
           '    END    AS    masters_grad_year'
           ' FROM    alum_rec    alum    INNER JOIN    id_rec            ids        ON    alum.id                =        ids.id'
           '                            LEFT JOIN    ('
           '                                SELECT prim_id, MAX(active_date) active_date'
           '                                FROM addree_rec'
           '                                WHERE style = "M"'
           '                                GROUP BY prim_id'
           '                            )                            prevmap    ON    ids.id                =        prevmap.prim_id'
           '                            LEFT JOIN    addree_rec        maiden    ON    maiden.prim_id        =        prevmap.prim_id'
           '                                                                AND    maiden.active_date    =        prevmap.active_date'
           '                                                                AND    maiden.style        =        "M"'
           '                            LEFT JOIN    aa_rec            email    ON    ids.id                =        email.id'
           '                                                                AND    email.aa            =        "EML2"'
           '                                                                AND    TODAY                BETWEEN email.beg_date    AND    NVL(email.end_date, TODAY)'
           '                            LEFT JOIN    aa_rec            aawork    ON    ids.id                =        aawork.id'
           '                                                                AND    aawork.aa            =        "WORK"'
           '                                                                AND    TODAY                BETWEEN    aawork.beg_date    AND    NVL(aawork.end_date, TODAY)'
           '                            LEFT JOIN    prog_enr_rec    progs    ON    ids.id                =        progs.id'
           '                                                                AND    progs.acst            =        "GRAD"'
           '                            LEFT JOIN    major_table        major1    ON    progs.major1        =       major1.major'
           '                            LEFT JOIN    major_table        major2    ON    progs.major2        =        major2.major'
           '                            LEFT JOIN   major_table     major3  ON  progs.major3        =       major3.major'
           '                            LEFT JOIN    conc_table        conc1    ON    progs.conc1            =        conc1.conc'
           '                            LEFT JOIN    conc_table        conc2    ON    progs.conc2            =        conc2.conc'
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
                     '                                        ELSE    prim.firstname'
                     '      END'
                     '    )    AS    firstName,'
                     '    TRIM('
                     '        CASE'
                     '            WHEN    rel.prim_id    =    %s    THEN    sec.lastname'
                     '                                        ELSE    prim.lastname'
                     '        END'
                     '    )    AS    lastName,'
                     '    TRIM('
                     '        CASE'
                     '            WHEN    rel.prim_id    =    %s    THEN    reltbl.sec_txt'
                     '                                        ELSE    reltbl.prim_txt'
                     '        END'
                     '    )    AS    relText'
                     ' FROM    relation_rec    rel    INNER JOIN    id_rec        prim    ON    rel.prim_id    =    prim.id'
                     '                            INNER JOIN    id_rec        sec        ON    rel.sec_id    =    sec.id'
                     '                            INNER JOIN    rel_table    reltbl    ON    rel.rel        =    reltbl.rel'
                     ' WHERE prim_id =   %s'
                     ' OR    sec_id  =   %s' % (student_id, student_id, student_id, student_id, student_id)
    )
    relatives = do_sql(relatives_sql)
    return relatives.fetchall()

def getMajors():
    major_sql = 'SELECT DISTINCT TRIM(major) AS major_code, TRIM(txt) AS major_name FROM major_table ORDER BY TRIM(txt)'
    majors = do_sql(major_sql)
    return majors.fetchall()

