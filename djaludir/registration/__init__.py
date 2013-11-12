SEARCH = """
    SELECT
        id_rec.id,profile_rec.birth_date,
        id_rec.firstname,
        id_rec.lastname, aname_rec.line1 as alt_name,id_rec.addr_line1,
        id_rec.addr_line2, id_rec.city, id_rec.st, NVL(id_rec.zip,"") as postal_code,
        id_rec.phone as homephone,
        email_rec.line1 as email,
        MIN(stu_acad_rec.yr) AS start_year, MAX(stu_acad_rec.yr) AS end_year,
        cvid_rec.ldap_name
    FROM
        id_rec
    LEFT JOIN
        cvid_rec on id_rec.id = cvid_rec.cx_id
    LEFT JOIN
        profile_rec on id_rec.id = profile_rec.id
    LEFT JOIN
        stu_acad_rec on
        (id_rec.id = stu_acad_rec.id AND stu_acad_rec.yr > 0)
    LEFT JOIN aa_rec as aname_rec on
        (id_rec.id = aname_rec.id AND aname_rec.aa = "ANDR")
    LEFT JOIN aa_rec as email_rec on
        (id_rec.id = email_rec.id AND email_rec.aa = "EML1")
    WHERE

"""
