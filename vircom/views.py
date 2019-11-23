# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from .models import Community, Post, DataType, Field, DataTypeObject
from django.http import Http404
from django.urls import reverse
import datetime
import json
import uuid
from django.core import serializers


# Create your views here.

# HOMEPAGE

def index(request):
    community_list = Community.objects.order_by('-pub_date')[:30]
    #template = loader.get_template('vircom/index.html')
    context = {
        'community_list': community_list,
    }
    return render(request, 'vircom/index.html', context)

# NEW COMMUNITY    

def new_community(request):    
    return render(request, 'vircom/new_community.html')

def create_community(request):
    name = request.POST['name']
    description = request.POST['description']
    tags = request.POST['tags']
    tags_array  = tags.split(",")
    tags_dict = {}
    tags_dict['tags'] = []
    for tag in tags_array:
        tags_dict['tags'].append(
            {
            "tag": tag
            }
        )
    #tags_json = json.dumps(tags_dict)
    community = Community(name=name, description=description, pub_date=datetime.datetime.now(),tags=tags_dict)
    if community.name == "" or community.description == "":
        return render(request, 'vircom/new_community.html', {
            'community': community,
            'error_message': "Name and Description fields cannot be empty.",
        })
    else:
        community.save()
        post = DataType (name="Default Post", community=community)
        post.save()
        title = Field(name="Title",field_type="Text",required="Yes", community=community,data_type=post)
        title.save()
        body = Field(name="Body",field_type="Long Text",required="Yes", community=community,data_type=post)
        body.save()
        return HttpResponseRedirect(reverse('vircom:index'))
    

# COMMUNITY DETAILS    

def community_detail(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    data_type_list = DataType.objects.filter(community=community)
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    post_list = Post.objects.filter(community=community).order_by('-pub_date')
    context = {
        'community': community,
        'post_list': post_list,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    return render(request, 'vircom/community_detail.html', context)

 #POST   

def new_post(request, community_name):        
    community = get_object_or_404(Community, name=community_name)
    context = {
        'community': community,
    }
    return render(request, 'vircom/new_post.html', context)

def create_post(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    title = request.POST['title']
    body = request.POST['body']
    post = Post(title=title, body=body, pub_date=datetime.datetime.now(),community=community)
    if post.title == "" or post.body == "":
        return render(request, 'vircom/new_post.html', {
            'community': community,
            'error_message': "Title and Body fields cannot be empty.",
        })
    else:
        post.save()
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

#DATA TYPE        

def new_data_type(request, community_name, fields = '{"fields":[]}'):        
    community = get_object_or_404(Community, name=community_name)
    if fields == '{"fields":[]}':
        context = {
        'community': community,
        'fields': fields,
        'field_list': '',
    }
    else:
        field_list = json.loads(fields)
        context = {
            'community': community,
            'fields': fields,
            'field_list': field_list,
        }
    return render(request, 'vircom/new_data_type.html', context) 

def create_data_type(request, community_id, fields):
    community = get_object_or_404(Community, pk=community_id)
    name = request.POST['name']
    data_type = DataType(name=name, community=community)
    data_type_list = DataType.objects.filter(community=community)
    for dt in data_type_list:
        if dt.name == name:
            return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'error_message': "There is a data type called " + name + " in this community.",
        })
    if data_type.name == "":
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'error_message': "Title field cannot be empty.",
        })  
    if fields == '{"fields":[]}':
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'error_message': "You need to add at least one custom field.",
        })
    else:
        data_type.save()
        fields_dict = {}
        fields_dict = json.loads(fields)
        for field in fields_dict['fields']:
            f = Field(name=field["name"],field_type=field["field_type"],required=field["required"], community=community,data_type=data_type)
            f.save()
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))           
    

def add_field(request, community_id, fields):
    community = get_object_or_404(Community, pk=community_id)
    name = request.POST["name"]
    field_type = request.POST["type"]
    required = request.POST["required"]
    if name == "":
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'error_message_fields': "Title field cannot be empty.",
        }) 
    else:     
        f = json.loads(fields)
        f['fields'].append({
            "name": name,
            "field_type": field_type,
            "required": required
        }) 
        fields = json.dumps(f)
    return HttpResponseRedirect(reverse('vircom:new_data_type', args=(community.name,fields)))

# DATA TYPE OBJECT    

def new_data_type_object(request, community_name, data_type_name):        
    community = get_object_or_404(Community, name=community_name)
    data_type = get_object_or_404(DataType, name=data_type_name, community=community)
    fields = Field.objects.filter(data_type=data_type,community=community)
    context = {
        'community': community,
        'data_type': data_type,
        'fields': fields
    }
    return render(request, 'vircom/new_data_type_object.html', context) 

def create_data_type_object(request, community_id, data_type_id):
    community = get_object_or_404(Community, pk=community_id)
    data_type = get_object_or_404(DataType, pk=data_type_id)
    fields = Field.objects.filter(data_type=data_type,community=community)
    f = {}
    f['fields'] = []
    for field in fields:
        field_id = str(field.pk)
        if request.POST[field_id] == "" or None and field.required == "Yes":
            return render(request, 'vircom/new_data_type_object.html', {
            'community': community,
            'data_type': data_type,
            'fields': fields,
            'error_message': "You cannot leave required fields empty.",
        }) 
        f['fields'].append(
            {
                "name": field.name,
                "field_type": field.field_type,
                "required": field.required,
                "value": request.POST[field_id]
            }
        )
    data_type_object = DataTypeObject(pub_date=datetime.datetime.now(), community=community, data_type=data_type, fields=f)
    data_type_object.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))     

def delete_post(request, community_id, post_id):  
    community = get_object_or_404(Community, pk=community_id)      
    post = DataTypeObject.objects.get(pk=post_id)
    post.delete()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def edit_post(request, community_name, post_id):  
    community = get_object_or_404(Community, name=community_name)
    post = DataTypeObject.objects.get(pk=post_id)
    context = {
        'community': community,
        'post': post,
    }
    return render(request, 'vircom/edit_post.html', context)

def change_post(request, community_id, post_id):
    community = get_object_or_404(Community, pk=community_id)
    post = DataTypeObject.objects.get(pk=post_id)
    f = {}
    f['fields'] = []
    for field in fields:
        field_id = str(field.pk)
        if request.POST[field_id] == "" or None and field.required == "Yes":
            return render(request, 'vircom/new_data_type_object.html', {
            'community': community,
            'data_type': data_type,
            'fields': fields,
            'error_message': "You cannot leave required fields empty.",
        }) 
        f['fields'].append(
            {
                "name": field.name,
                "field_type": field.field_type,
                "required": field.required,
                "value": request.POST[field_id]
            }
        )
    post.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))     

