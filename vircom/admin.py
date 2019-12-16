# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Community, DataType, DataTypeObject, MediaFile, VircomUser, WikiItem

# Register your models here.
admin.site.register(Community)
admin.site.register(DataType)
admin.site.register(DataTypeObject)
admin.site.register(MediaFile)
admin.site.register(VircomUser)
admin.site.register(WikiItem)