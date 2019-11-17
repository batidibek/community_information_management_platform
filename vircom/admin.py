# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Community, Post, DataType, DataTypeObject

# Register your models here.
admin.site.register(Community)
admin.site.register(Post)
admin.site.register(DataType)

