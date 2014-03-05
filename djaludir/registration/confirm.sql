SELECT
    id_rec.id,profile_rec.birth_date,
    id_rec.firstname, aname_rec.line1,
    id_rec.lastname, SUBSTRING(id_rec.ss_no FROM 8 FOR 4) as ss_no,
    cvid_rec.ldap_name
FROM
    id_rec
LEFT JOIN
    cvid_rec on id_rec.id = cvid_rec.cx_id
LEFT JOIN aa_rec as aname_rec on
    (id_rec.id = aname_rec.id AND aname_rec.aa = "ANDR")
LEFT JOIN
    profile_rec on id_rec.id = profile_rec.id
WHERE
    SUBSTRING(id_rec.ss_no FROM 8 FOR 4)="0000"
AND
    (profile_rec.birth_date = "02/02/1974" OR profile_rec.birth_date is null)
