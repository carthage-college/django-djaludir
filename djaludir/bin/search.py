from djzbar.utils.informix import do_sql

data = {'first_name':'steve','last_name':'kirk','email':'','college_id':'','dob':'',}

SEARCH = """
    SELECT
        id_rec.id, profile_rec.birth_date,
        id_rec.firstname,
        id_rec.lastname, aname_rec.line1 as alt_name,id_rec.addr_line1,
        id_rec.addr_line2, id_rec.city, id_rec.st, NVL(id_rec.zip,"") as postal_code,
        id_rec.phone as homephone,
        email_rec.line1 as email,
        cvid_rec.ldap_name
    FROM
        id_rec
    LEFT JOIN
        cvid_rec on id_rec.id = cvid_rec.cx_id
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

if data["email"]:
    where+= ' AND'
    where+= ' email_rec.line1 = "%s"' % data["email"]
if data["college_id"]:
    where+= ' AND'
    where+= ' id_rec.id = "%s"' % data["college_id"]
if data["dob"]:
    where+= ' AND'
    where+= ' profile_rec.birth_date = "%s"' % data["dob"].strftime("%m/%d/%Y")

xsql = SEARCH+ where
xsql += ' ORDER BY id_rec.lastname, id_rec.firstname, profile_rec.birth_date'
results = do_sql(xsql)

objs = do_sql(xsql)

for obj in objs:
    print obj

