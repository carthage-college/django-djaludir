from djzbar.utils.informix import do_sql

sql = """
SELECT MIN(yr) AS start_year, MAX(yr) AS end_year FROM stu_acad_rec WHERE id = "934256" AND yr > 0
"""

objs = do_sql(sql)

for obj in objs:
    print obj

