# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Base(models.Model):
    """
    Abstract base class for all data models
    """

    # meta
    user = models.ForeignKey(
        User, verbose_name="Created by", editable=settings.DEBUG,
        related_name='%(app_label)s_%(class)s_created_by',
    )
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    approved_at = models.DateTimeField(
        "Date Approved", auto_now=True
    )
    updated_by = models.ForeignKey(
        User, verbose_name="Updated by", editable=settings.DEBUG,
        related_name='%(app_label)s_%(class)s_updated_by',
    )
    approved = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering  = ['-created_at']
        get_latest_by = 'created_at'


class Activity(Base):
    """
    Activities like student organizations, clubs, or sport
    """

    code = models.CharField(max_length=4, null=True, blank=True)
    text = models.CharField(max_length=32, null=True, blank=True)

    def __unicode__(self):
        return "[{}] {}".format(self.code, self.text)

    def get_slug(self):
        return 'activity'


class Address(Base):
    """
    Addresses for home and work
    """

    aa = models.CharField(max_length=4, null=True, blank=True)
    address_line1 = models.CharField(max_length=64, null=True, blank=True)
    address_line2 = models.CharField(max_length=64, null=True, blank=True)
    address_line3 = models.CharField(max_length=64, null=True, blank=True)

    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=3, null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True)

    def __unicode__(self):
        return "{} {} {} {} {} {} {}".format(
            self.address_line1, self.address_line2, self.address_line3,
            self.city, self.state, self.zip, self.country
        )

    def get_slug(self):
        return 'address'


class Alumni(Base):
    """
    Alumni vitals
    """

    alt_name = models.CharField(max_length=32, null=True, blank=True)
    suffix = models.CharField(max_length=10, null=True, blank=True)
    prefix = models.CharField(max_length=10, null=True, blank=True)
    email = models.CharField(max_length=254, null=True, blank=True)
    maiden_name = models.CharField(max_length=32, null=True, blank=True)
    degree = models.CharField(max_length=4, null=True, blank=True)
    class_year = models.CharField(max_length=4, null=True, blank=True)
    business_name = models.CharField(max_length=64, null=True, blank=True)
    major1 = models.CharField(max_length=4, null=True, blank=True)
    major2 = models.CharField(max_length=4, null=True, blank=True)
    major3 = models.CharField(max_length=4, null=True, blank=True)
    masters_grad_year = models.CharField(max_length=4, null=True, blank=True)
    job_title = models.CharField(max_length=64, null=True, blank=True)

    def __unicode__(self):
        return u"{}, {}".format(
            self.user.last_name, self.user.first_name
        )

    def get_slug(self):
        return 'alumni'


class Privacy(Base):
    """
    Privacy settings for the various data models
    """

    fieldname = models.CharField(max_length=32, null=True, blank=True)
    display = models.BooleanField(default=False)

    def __unicode__(self):
        return "[{}] {}".format(self.fieldname, self.display)

    def get_slug(self):
        return 'privacy'


class Relative(Base):
    """
    Activities like student organizations, clubs, or sport
    """

    relation_code = models.CharField(max_length=8, null=True, blank=True)
    first_name = models.CharField(max_length=32, null=True, blank=True)
    last_name = models.CharField(max_length=32, null=True, blank=True)
    primary = models.BooleanField(default=False)

    def __unicode__(self):
        return "[{}] {}, {}".format(
            self.relation_code, self.last_name, self.first_name
        )

    def get_slug(self):
        return 'relative'
