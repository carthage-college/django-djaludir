RELATIVES_ORIG = '''
    SELECT
        TRIM(
            CASE
                WHEN    rel.prim_id = {student_number}
                THEN    sec.firstname
                ELSE    prim.firstname
            END
        ) AS firstName,
        TRIM(
            CASE
                WHEN    rel.prim_id = {student_number}
                THEN    sec.lastname
                ELSE    prim.lastname
            END
       ) AS lastName,
       TRIM(
            CASE
                WHEN    rel.prim_id = {student_number}
                THEN    reltbl.sec_txt
                ELSE    reltbl.prim_txt
            END
        ) AS relText,
        TRIM(reltbl.rel) ||
            CASE
                WHEN    rel.prim_id = {student_number}
                THEN    "2"
                ELSE    "1"
            END
        AS relCode
    FROM
        relation_rec rel
    INNER JOIN
        id_rec prim
    ON
        rel.prim_id = prim.id
    INNER JOIN
        id_rec sec
    ON
        rel.sec_id = sec.id
    INNER JOIN
        rel_table reltbl
    ON
        rel.rel = reltbl.rel
    WHERE
        TODAY BETWEEN
            rel.beg_date
        AND
            NVL(rel.end_date, TODAY)
    AND
        rel.rel IN ("AUNN","COCO","GPGC","HW","HWNI","PC","SBSB")
    AND
        (prim_id = {student_number} OR sec_id = {student_number})
'''.format

RELATIVES_TEMP = '''
    SELECT
        TRIM(fname) AS fname, TRIM(lname) AS lname,
        CASE
        WHEN
            TRIM(relcode) = 'HW'   AND alum_primary = 'N' THEN 'Husband'
        WHEN
            TRIM(relcode) = 'HW'   AND alum_primary = 'Y' THEN 'Wife'
        WHEN
            TRIM(relcode) = 'PC'   AND alum_primary = 'N' THEN 'Parent'
        WHEN
            TRIM(relcode) = 'PC'   AND alum_primary = 'Y' THEN 'Child'
        WHEN
            TRIM(relcode) = 'GPGC' AND alum_primary = 'N' THEN 'Grandparent'
        WHEN
            TRIM(relcode) = 'GPGC' AND alum_primary = 'Y' THEN 'Grandchild'
        WHEN
            TRIM(relcode) = 'AUNN' AND alum_primary = 'N' THEN 'Aunt/Uncle'
        WHEN
            TRIM(relcode) = 'AUNN' AND alum_primary = 'Y' THEN 'Niece/Nephew'
        WHEN
            TRIM(relcode) = 'SBSB' THEN 'Sibling'
        WHEN
            TRIM(relcode) = 'COCO' THEN 'Cousin'
        ELSE
            TRIM(relcode)
        END AS
            relcode
    FROM
        stg_aludir_relative
    WHERE
        id = {student_number} AND NVL(approved, "") = ""
'''.format

ALUMNA = '''
SELECT DISTINCT
    ids.id AS carthage_id,
    TRIM(ids.firstname) AS fname,
    TRIM(ids.lastname) AS lname,
    TRIM(ids.suffix) AS suffix,
    TRIM(INITCAP(ids.title)) AS prefix,
    TRIM(NVL(email.line1,"")) email,
    CASE
        WHEN NVL(ids.decsd, "N") = "Y"
        THEN 1
    END AS is_deceased,
    TRIM(NVL(maiden.lastname,"")) AS birth_lname,
    TRIM(NVL(progs.deg,"")) AS degree,
    CASE
        WHEN TRIM(progs.deg) IN ("BA","BS")
        THEN alum.cl_yr
    END AS class_year,
    TRIM(NVL(aawork.line1, "")) AS business_name,
    TRIM(NVL(aawork.line2,"")) AS business_address,
    TRIM(NVL(aawork.line3,"")) AS business_address2,
    TRIM(NVL(aawork.city,"")) AS business_city,
    TRIM(aawork.st) AS business_state,
    TRIM(NVL(aawork.zip,"")) AS business_zip,
    TRIM(aawork.ctry) AS business_country,
    TRIM(NVL(aawork.phone,"")) AS business_phone,
    TRIM(ids.addr_line1) AS home_address1,
    TRIM(ids.addr_line2) AS home_address2,
    TRIM(ids.addr_line3) AS home_address3,
    TRIM(ids.city) AS home_city,
    TRIM(ids.st) AS home_state,
    TRIM(ids.zip) AS home_zip,
    TRIM(ids.ctry) AS home_country, TRIM(ids.phone) AS home_phone,
    TRIM(
        CASE
              WHEN TRIM(progs.deg) IN ("BA","BS")
              THEN major1.txt
              ELSE conc1.txt
        END
    ) AS major1,
    TRIM(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN major2.txt
            ELSE conc2.txt
        END
    ) AS major2,
    TRIM(
        CASE
            WHEN TRIM(progs.deg) IN ("BA","BS")
            THEN major3.txt
            ELSE ""
        END
    ) AS major3,
    CASE
        WHEN TRIM(progs.deg) NOT IN ("BA","BS")
        THEN alum.cl_yr
        ELSE 0
    END AS masters_grad_year,
    "" AS job_title
FROM
    alum_rec alum
    INNER JOIN
        id_rec ids          ON  alum.id = ids.id
    LEFT JOIN (
        SELECT   prim_id, MAX(active_date) active_date
        FROM     addree_rec
        WHERE    style = "M"
        GROUP BY prim_id
    )
        prevmap             ON  ids.id              = prevmap.prim_id
    LEFT JOIN
        addree_rec maiden   ON  maiden.prim_id      = prevmap.prim_id
                            AND maiden.active_date  = prevmap.active_date
                            AND maiden.style        = "M"
    LEFT JOIN
        aa_rec email        ON  ids.id              = email.id
                            AND email.aa            = "EML2"
                            AND TODAY
                                BETWEEN
                                    email.beg_date
                                AND
                                    NVL(
                                        email.end_date,
                                        TODAY
                                    )
    LEFT JOIN
        aa_rec aawork       ON  ids.id              = aawork.id
                            AND aawork.aa           = "WORK"
                            AND TODAY
                                BETWEEN
                                    aawork.beg_date
                                AND
                                    NVL(
                                        aawork.end_date,
                                        TODAY
                                    )
    LEFT JOIN
        prog_enr_rec progs  ON  ids.id          = progs.id
                            AND progs.acst      = "GRAD"
    LEFT JOIN
        major_table major1  ON  progs.major1    = major1.major
    LEFT JOIN
        major_table major2  ON  progs.major2    = major2.major
    LEFT JOIN
        major_table major3  ON  progs.major3    = major3.major
    LEFT JOIN
        conc_table conc1    ON  progs.conc1     = conc1.conc
    LEFT JOIN
        conc_table conc2    ON  progs.conc2     = conc2.conc
WHERE
    ids.id = {sid}
{deceased}
'''.format
