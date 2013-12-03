SEARCH = """
    SELECT
        id_rec.id,profile_rec.birth_date,
        id_rec.firstname, aname_rec.line1,
        maiden.lastname AS maiden_name,
        id_rec.lastname, id_rec.city, id_rec.st,
        NVL(id_rec.zip,"") as postal_code,
        id_rec.phone, email_rec.line1 as email, cvid_rec.ldap_name,
        MIN(stu_acad_rec.yr) AS start_year, MAX(stu_acad_rec.yr) AS end_year
    FROM
        id_rec
    LEFT JOIN
        cvid_rec on id_rec.id = cvid_rec.cx_id
    LEFT JOIN
        profile_rec on id_rec.id = profile_rec.id
    LEFT JOIN (
        SELECT prim_id, MAX(active_date) active_date
        FROM addree_rec
        WHERE style = "M"
        GROUP BY prim_id
        ) prevmap ON id_rec.id = prevmap.prim_id
    LEFT JOIN
        addree_rec maiden ON maiden.prim_id = prevmap.prim_id AND maiden.active_date = prevmap.active_date AND maiden.style = "M"
    LEFT JOIN
        stu_acad_rec on
        (id_rec.id = stu_acad_rec.id AND stu_acad_rec.yr > 0)
    LEFT JOIN aa_rec as aname_rec on
        (id_rec.id = aname_rec.id AND aname_rec.aa = "ANDR")
    LEFT JOIN aa_rec as email_rec on
        (id_rec.id = email_rec.id AND email_rec.aa = "EML1")
    WHERE
"""
SEARCH_GROUP_BY = """
    GROUP by id,birth_date,firstname,line1,maiden_name,lastname,city,st,postal_code,phone,email,ldap_name
"""
SEARCH_ORDER_BY = """
    ORDER BY id_rec.lastname, id_rec.firstname, profile_rec.birth_date
"""

'''
SELECT DISTINCT
    alum.cl_yr AS class_year, ids.firstname, maiden.lastname AS maiden_name,
    ids.lastname, ids.id, LOWER(ids.lastname) AS sort1,
    LOWER(ids.firstname) AS sort2
FROM
    alum_rec alum
INNER JOIN
    id_rec ids ON alum.id = ids.id
LEFT JOIN (
    SELECT prim_id, MAX(active_date) active_date
    FROM addree_rec
    WHERE style = "M"
    GROUP BY prim_id
    ) prevmap ON ids.id = prevmap.prim_id
LEFT JOIN
    addree_rec maiden ON maiden.prim_id = prevmap.prim_id AND maiden.active_date = prevmap.active_date AND maiden.style = "M"
WHERE
    LOWER(TRIM(ids.lastname::varchar(250))) LIKE "%williams%"
AND
    LOWER(TRIM(ids.firstname::varchar(250))) LIKE "%gary%"
AND
    LOWER(TRIM(alum.cl_yr::varchar(250))) LIKE "%0%"
ORDER BY
    LOWER(ids.lastname), LOWER(ids.firstname), alum.cl_yr
'''
