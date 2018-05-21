# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.ext.hybrid import hybrid_method

Base = declarative_base()


class AlumniActivity(Base):
    """
    Alumni activities like student organizations, clubs, or sport
    """

    __tablename__ = 'stg_aludir_activity'

    # core
    activity_no = Column(BigInteger, primary_key=True)
    id = Column(Integer, nullable=False)
    activitycode = Column(String)
    activitytext = Column(String)
    # meta
    submitted_on = Column(Date)
    approved = Column(String)
    approved_date = Column(Date)

    def __repr__(self):
        return "[{}] {}".format(self.activitycode, self.activitytext)

    def get_slug(self):
        return 'activity'


class AlumniAddress(Base):
    """
    Alumni addresses for home and work
    """

    __tablename__ = 'stg_aludir_address'

    # core
    aa_no = Column(BigInteger, primary_key=True)
    aa = Column(String)
    id = Column(Integer, nullable=False)
    address_line1 = Column(String)
    address_line2 = Column(String)
    address_line3 = Column(String)
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    country = Column(String)
    phone = Column(String)
    # meta
    submitted_on = Column(Date)
    approved = Column(String)
    approved_date = Column(Date)

    def __repr__(self):
        return "{} {} {} {} {} {} {}".format(
            self.address_line1, self.address_line2, self.address_line3,
            self.city, self.state, self.zip, self.country
        )

    def get_slug(self):
        return 'address'


class Alumni(Base):
    """
    Alumni vital stats
    """

    __tablename__ = 'stg_aludir_alumni'

    # core
    alum_no = Column(BigInteger, primary_key=True)
    id = Column(Integer, nullable=False)
    fname = Column(String)
    aname = Column(String)
    lname_line3 = Column(String)
    suffix = Column(String)
    prefix = Column(String)
    email = Column(String)
    maidenname = Column(String)
    degree = Column(String)
    class_year = Column(Integer)
    business_name = Column(String)
    major1 = Column(String)
    major2 = Column(String)
    major3 = Column(String)
    masters_grad_year = Column(Integer)
    job_title = Column(String)
    # meta
    submitted_on = Column(Date)
    approved = Column(String)
    approved_date = Column(Date)

    def __repr__(self):
        return "{}, {}".format(
            self.lname, self.fname
        )

    def get_slug(self):
        return 'alumni'


class AlumniPrivacy(Base):
    """
    Alumni privacy settings for the various data models
    """

    __tablename__ = 'stg_aludir_privacy'

    # core
    priv_no = Column(BigInteger, primary_key=True)
    id = Column(Integer, nullable=False)
    fieldname = Column(String)
    display = Column(String)
    # meta
    lastupdated = Column(Date)

    def __repr__(self):
        return "[{}] {}".format(self.fieldname, self.display)

    def get_slug(self):
        return 'privacy'

