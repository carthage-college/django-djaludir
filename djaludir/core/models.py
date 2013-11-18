# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models, connection
from django.contrib.auth.models import User

class Organizations(models.Model):
    abbr = models.CharField(max_length="4", blank=False, null=False)
    name = models.CharField(max_length="32", blank=False, null=False)
    active_date = models.DateField(blank=True, null=True)
    inactive_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name


class Athletics(models.Model):
    abbr = models.CharField(max_length="4", blank=False, null=False)
    name = models.CharField(max_length="32", blank=False, null=False)
    active_date = models.DateField(blank=True, null=True)
    inactive_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

class Alumni(models.Model):
    """
    Model: Alumni
    """
    carthage_id = models.IntegerField(verbose_name="Carthage ID#")
    fname = models.CharField(max_length=32, verbose_name="First name")
    lname = models.CharField(max_length=50, verbose_name="Last name")
    suffix = models.CharField(max_length=4, blank=True, null=True)
    prefix = models.CharField(max_length=4, blank=True, null=True)
    email = models.EmailField(max_length=64, blank=True, null=True)
    is_deceased = models.BooleanField()
    birth_fname = models.CharField(max_length=32, verbose_name="Birth first name", blank=True, null=True)
    birth_lname = models.CharField(max_length=50, verbose_name="Birth last name", blank=True, null=True)
    degree = models.CharField(max_length=4, blank=True, null=True)
    class_year = models.PositiveSmallIntegerField(blank=True, null=True)
    job_title = models.CharField(max_length=64, blank=True, null=True)
    business_name = models.CharField(max_length=64, blank=True, null=True)
    business_address = models.CharField(max_length=64, blank=True, null=True)
    business_city = models.CharField(max_length=50, blank=True, null=True)
    business_state = models.CharField(max_length=2, blank=True, null=True)
    business_zip = models.CharField(max_length=10, blank=True, null=True)
    business_country = models.CharField(max_length=3, blank=True, null=True)
    business_phone = models.CharField(max_length=12, blank=True, null=True)
    home_address1 = models.CharField(max_length=64, verbose_name="Home Address Line 1", blank=True, null=True)
    home_address2 = models.CharField(max_length=64, verbose_name="Home Address Line 2", blank=True, null=True)
    home_address3 = models.CharField(max_length=64, verbose_name="Home Address Line 3", blank=True, null=True)
    home_city = models.CharField(max_length=50, blank=True, null=True)
    home_state = models.CharField(max_length=2, blank=True, null=True)
    home_zip = models.CharField(max_length=10, blank=True, null=True)
    home_country = models.CharField(max_length=3, blank=True, null=True)
    home_phone = models.CharField(max_length=12, blank=True, null=True)
    major1 = models.CharField(max_length=35, verbose_name="Major 1", blank=True, null=True)
    major2 = models.CharField(max_length=35, verbose_name="Major 2", blank=True, null=True)
    major3 = models.CharField(max_length=35, verbose_name="Major 3", blank=True, null=True)
    honorary_degree = models.CharField(max_length=255, verbose_name="Honorary Degree Received", blank=True, null=True)
    distinguished_alumni = models.CharField(max_length=255, verbose_name="Distinguished Alumni Award Received", blank=True, null=True)
    masters_grad_year = models.CharField(max_length=4,verbose_name="Masters Graduation Year", blank=True, null=True)
    student_organizations = models.ManyToManyField(Organizations, related_name="org+")
    athletic_teams = models.ManyToManyField(Athletics, related_name="team+")
    user = models.ForeignKey(User, blank=False, null=False)
    # meta
    created_by = models.ForeignKey(User,verbose_name="Created by",related_name="created_by",editable=False,null=True,blank=True)
    updated_by = models.ForeignKey(User,verbose_name="Updated by",related_name="updated_by",editable=False,null=True,blank=True)
    created_at = models.DateTimeField("Date Created",auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated",auto_now=True)

    class Meta:
        ordering = ['-created_at']
        get_latest_by = 'created_at'

    def __unicode__(self):
        return ("%s %s") % (self.fname, self.lname)

    def get_privacy(self):
        try:
            privacy = Privacy.objects.get(person = self.id)
        except:
            privacy = Privacy(person=Person(),info=[])
        return privacy

    def may_display(self,field):
        persons_privacy = self.get_privacy()
        return field not in persons_privacy.info

    def relatives(self):
        num_rels = 0
        if self.relation_name1 != '':
            num_rels = num_rels + 1
        if self.relation_name2 != '':
            num_rels = num_rels + 1
        if self.relation_name3 != '':
            num_rels = num_rels + 1
        if self.relation_name4 != '':
            num_rels = num_rels + 1
        if self.relation_name5 != '':
            num_rels = num_rels + 1
        if self.relation_name6 != '':
            num_rels = num_rels + 1
        if self.relation_name7 != '':
            num_rels = num_rels + 1
        if self.relation_name8 != '':
            num_rels = num_rels + 1
        if self.relation_name9 != '':
            num_rels = num_rels + 1
        if self.relation_name10 != '':
            num_rels = num_rels + 1
        if self.relation_name11 != '':
            num_rels = num_rels + 1
        return num_rels

    def organizations(self):
        num_orgs = 0
        if self.student_organization1 != '':
            num_orgs = num_orgs + 1
        if self.student_organization2 != '':
            num_orgs = num_orgs + 1
        if self.student_organization3 != '':
            num_orgs = num_orgs + 1
        if self.student_organization4 != '':
            num_orgs = num_orgs + 1
        if self.student_organization5 != '':
            num_orgs = num_orgs + 1
        return num_orgs

    def teams(self):
        num_teams = 0
        if self.athletic_team1 != '':
            num_teams = num_teams + 1
        if self.athletic_team2 != '':
            num_teams = num_teams + 1
        if self.athletic_team3 != '':
            num_teams = num_teams + 1
        if self.athletic_team4 != '':
            num_teams = num_teams + 1
        if self.athletic_team5 != '':
            num_teams = num_teams + 1
        return num_teams

class Relatives(models.Model):
    alum = models.ForeignKey(Alumni, blank=False, null=False)
    RELATION_CHOICES = (
        ('HW1','Wife'),
        ('HW2','Husband'),
        ('PC1','Child'),
        ('PC2','Parent'),
        ('SBSB','Sibling'),
        ('GPGC1','Grandchild'),
        ('GPGC2','Grandparent'),
        ('AUNN1','Niece/Nephew'),
        ('AUNN2','Aunt/Uncle'),
        ('COCO','Cousin'),
    )
    relation_type = models.CharField(max_length="5", blank=False, null=False, choices=RELATION_CHOICES)
    fname = models.CharField(max_length="32", verbose_name="Relation First Name", blank=False, null=False)
    lname = models.CharField(max_length="50", verbose_name="Relation Last Name", blank=True, null=True)
    dob = models.DateField(verbose_name="Relation Date of Birth", blank=True, null=True)

    def __str__(self):
        return ("%s %s") % (self.fname, self.lname)


class Privacy(models.Model):
    alumna = models.ForeignKey(Alumni, blank=False, null=False)
    info = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s hiding %s" % (self.alumna, self.info)

# Globals

import datetime

YEARS =  [(x, x) for x in reversed(xrange(1926,datetime.date.today().year +1))]

