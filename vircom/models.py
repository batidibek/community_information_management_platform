# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid
import datetime
from django.contrib.postgres.fields import ArrayField, JSONField

# Create your models here.
class Community(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank = True)
    tags = JSONField()
    pub_date = models.DateTimeField('date published')
    #User who created, datatypes etc.
    def __str__(self):
        return self.name       

class DataType(models.Model):   
    name = models.CharField(max_length=200)
    community = models.ForeignKey(Community, on_delete=models.PROTECT)
    fields = JSONField()
    def __str__(self):
        return self.name   

class DataTypeObject(models.Model):
    data_type = models.ForeignKey(DataType, on_delete=models.PROTECT)
    fields = JSONField()
    pub_date = models.DateTimeField('date published')
    community = models.ForeignKey(Community, on_delete=models.PROTECT) 
    # def __str__(self):
    #         return self.title

    
    

