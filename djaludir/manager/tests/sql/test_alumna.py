from django.conf import settings
from django.test import TestCase

from djaludir.core.sql import ALUMNA, ALUMNA_TEMP, SEARCH

from djtools.utils.logging import seperator
from djzbar.utils.informix import do_sql


class ManagerAlumnaTestCase(TestCase):

    def setUp(self):
        self.debug = settings.INFORMIX_DEBUG
        self.earl = settings.INFORMIX_EARL
        self.cid = settings.TEST_USER_COLLEGE_ID
        self.cid_null = 666

    def test_alumna(self):

        print("\n")
        print("test alumna select statement")
        print(seperator())

        sql = ALUMNA(cid = self.cid, deceased = '')
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertGreaterEqual(len(alumna), 1)

    def test_alumna_invalid(self):

        print("\n")
        print("test alumna select statement with invalid college ID")
        print(seperator())

        sql = ALUMNA(cid = self.cid_null, deceased = '')
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertEqual(len(alumna), 0)

    def test_alumna_temp(self):

        print("\n")
        print("test alumna temp table select statement")
        print(seperator())

        sql = ALUMNA_TEMP(cid = self.cid)
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertGreaterEqual(len(alumna), 1)

    def test_alumna_temp_invalid(self):

        print("\n")
        print("test alumna select statement with invalid college ID")
        print(seperator())

        sql = ALUMNA_TEMP(cid = self.cid_null)
        print(sql)

        alumna = do_sql(sql, self.debug, self.earl).fetchall()

        print(alumna)

        self.assertEqual(len(alumna), 0)

    def test_search(self):

        print("\n")
        print("test search select statement")
        print(seperator())

        append = '''
            LEFT JOIN
                stg_aludir_privacy per_priv
            ON
                ids.id = per_priv.id
            AND
                per_priv.fieldname = "Personal"
            WHERE
                LOWER(TRIM(ids.lastname::varchar(250))) LIKE "%%marx%%"
            AND
                NVL(per_priv.display, "N") = "N"
            AND
                holds.hld_no IS NULL
            GROUP BY
                class_year, fname, aname, maiden_name, lastname, id, email,
                sort1, sort2
            ORDER BY
                lastname, fname, alum.cl_yr
        '''

        sql = '{} {}'.format(SEARCH, append)
        print(sql)

        objects = do_sql(sql, self.debug, self.earl).fetchall()

        print(objects)

        self.assertGreaterEqual(len(objects), 1)

