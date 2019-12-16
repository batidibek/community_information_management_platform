# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid
import datetime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.auth.models import User

# Create your models here.
class Community(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank = True)
    tags = JSONField()
    pub_date = models.DateTimeField('date published')
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    def __str__(self):
        return self.name       

class DataType(models.Model):   
    name = models.CharField(max_length=200)
    community = models.ForeignKey(Community, on_delete=models.PROTECT)
    fields = JSONField()
    is_archived = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    def __str__(self):
        return self.community.name + "-" + self.name   

class DataTypeObject(models.Model):
    data_type = models.ForeignKey(DataType, on_delete=models.PROTECT)
    fields = JSONField()
    pub_date = models.DateTimeField('date published')
    community = models.ForeignKey(Community, on_delete=models.PROTECT) 
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    def __str__(self):
        return self.community.name + "-" + self.data_type.name + "-" + str(self.pk) 

class MediaFile(models.Model):
    upload = models.FileField(upload_to='uploads')
    url = models.TextField(blank = True)

class VircomUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    joined_communities = ArrayField(models.IntegerField(), blank=True, null=True)
    #data_types = ArrayField(models.IntegerField())
    #posts = ArrayField(models.IntegerField())
    def __str__(self):
        return self.user.username  

class WikiItem(models.Model):
    qid = models.CharField(max_length=200, unique=True) 
    label = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank = True)
    url = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.label
    

