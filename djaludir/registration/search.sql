SELECT
    id_rec.id, profile_rec.birth_date,
    id_rec.firstname,
    id_rec.lastname, aname_rec.line1 as alt_name,id_rec.addr_line1,
    id_rec.addr_line2, id_rec.city, id_rec.st, NVL(id_rec.zip,'') as postal_code,
    id_rec.phone as homephone,
    email_rec.line1 as email
FROM
    id_rec
LEFT JOIN
    profile_rec on id_rec.id = profile_rec.id
LEFT JOIN aa_rec as aname_rec on
    (id_rec.id = aname_rec.id AND aname_rec.aa = "ANDR")
LEFT JOIN aa_rec as email_rec on
    (id_rec.id = email_rec.id AND email_rec.aa = "EML1")
WHERE
    ( lower(id_rec.firstname) like "%john%" OR lower(aname_rec.line1) like "%john%" )
AND
    lower(id_rec.lastname) = "smith"
AND
    ( id_rec.zip like "%60091%" or NVL(id_rec.zip,'') = '' )
AND
    (profile_rec.birth_date = "1974-02-02" or profile_rec.birth_date is null);


SELECT count(*) FROM id_rec WHERE id_rec.zip = '';
