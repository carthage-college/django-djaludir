from djzbar.utils.informix import do_sql
from djaludir.registration import SEARCH, SEARCH_ORDER_BY, SEARCH_GROUP_BY

#data = {'first_name':'gary','last_name':'williams','email':'','college_id':'','dob':'',}
data = {'first_name':'susan','last_name':'blust','email':'','college_id':'831458','dob':'',}

where = (' ( lower(id_rec.firstname) like "%%%s%%" OR'
         ' lower(aname_rec.line1) like "%%%s%%" )'
         % (data["first_name"].lower(),data["first_name"].lower()))
where += ' AND'
where += (' lower(id_rec.lastname) = "%s"'
          % (data['last_name'].lower()))
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
xsql += SEARCH_GROUP_BY
xsql += SEARCH_ORDER_BY

print xsql

objs = do_sql(xsql, key="debug")

print objs

for obj in objs:
    print obj

