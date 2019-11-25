# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from .models import Community, DataType, DataTypeObject
from django.http import Http404
from django.urls import reverse
import datetime
import json
import uuid
from django.core import serializers
from django.http import JsonResponse


# Create your views here.

# HOMEPAGE

def index(request):
    community_list = Community.objects.order_by('-pub_date')[:30]
    #template = loader.get_template('vircom/index.html')
    context = {
        'community_list': community_list,
    }
    return render(request, 'vircom/index.html', context)

# COMMUNITY    

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
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    return render(request, 'vircom/community_detail.html', context)

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
    data_type = DataType(name=name, community=community, fields={})
    data_type_list = DataType.objects.filter(community=community)
    field_list = json.loads(fields)
    for dt in data_type_list:
        if dt.name == name:
            return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'field_list': field_list,
            'error_message': "There is a data type called " + name + " in this community.",
        })
    if data_type.name == "":
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'field_list': field_list,
            'error_message': "Title field cannot be empty.",
        })  
    if fields == '{"fields":[]}':
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'field_list': field_list,
            'error_message': "You need to add at least one custom field.",
        })
    else:
        fields_dict = {}
        fields_dict = json.loads(fields)
        data_type.fields = fields_dict
        data_type.save()
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))           
    

def add_field(request, community_id, fields):
    community = get_object_or_404(Community, pk=community_id)
    name = request.POST["name"]
    field_type = request.POST["type"]
    required = request.POST["required"]
    field_list = json.loads(fields)
    if name == "":
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'fields': fields,
            'field_list': field_list,
            'error_message_fields': "Field Name cannot be empty.",
        }) 
    else:     
        for field in field_list['fields']:
            if name == field['name']:
                return render(request, 'vircom/new_data_type.html', {
                    'community': community,
                    'fields': fields,
                    'field_list': field_list,
                    'error_message_fields': "You cannot use same field name twice.",
                }) 
        field_list['fields'].append({
            "name": name,
            "field_type": field_type,
            "required": required,
        }) 
        fields = json.dumps(field_list)
    return HttpResponseRedirect(reverse('vircom:new_data_type', args=(community.name,fields)))

def remove_field(request, community_id, fields, field_name):  
    community = get_object_or_404(Community, pk=community_id)
    f = json.loads(fields)
    counter = 0
    for field in f['fields']:
        if field['name'] == field_name:
            del f['fields'][counter]
            break
        counter = counter + 1
    fields = json.dumps(f)        
    return HttpResponseRedirect(reverse('vircom:new_data_type', args=(community.name,fields)))

def delete_data_type(request, community_id, data_type_id):    
    community = get_object_or_404(Community, pk=community_id)
    data_type = DataType.objects.get(pk=data_type_id)
    data_type.is_archived = True
    data_type.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def edit_data_type(request, community_name, data_type_name):  
    community = get_object_or_404(Community, name=community_name)
    data_type = DataType.objects.get(name=data_type_name, community=community)
    field_list = data_type.fields
    context = {
        'community': community,
        'data_type': data_type,
        'field_list': field_list,
    }
    return render(request, 'vircom/edit_data_type.html', context)

#not finished
def change_data_type(request, community_id, data_type_id):
    community = get_object_or_404(Community, pk=community_id)
    data_type = DataType.objects.get(pk=data_type_id, community=community)
    field_list = data_type.fields
    f = {}
    f['fields'] = []
    name = request.POST['title']
    print(dict(request.POST.lists()))
    response = dict(request.POST.lists())
    data_type_list = DataType.objects.filter(community=community)
    if request.POST.get('name') == None:
        return render(request, 'vircom/edit_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message_fields': "You need to add at least one field.",
        })
    for dt in data_type_list:
        if dt.name == name and dt.name != data_type.name:
            return render(request, 'vircom/edit_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message': "There is a data type called " + name + " in this community.",
        })
    if data_type.name == "":
        return render(request, 'vircom/edit_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message': "Title field cannot be empty.",
        }) 
    else:
        data_type.name = name
    for key in range(len(response['name'])):
        print(key)
        print(response['name'][key])
        if response['name'][key] == "":
            return render(request, 'vircom/edit_data_type.html', {
                'community': community,
                'data_type': data_type,
                'field_list': field_list,
                'error_message_fields': "Field Name cannot be empty.",
            }) 
        else:     
            for field in f['fields']:
                if response['name'][key] == field['name']:
                    return render(request, 'vircom/edit_data_type.html', {
                        'community': community,
                        'data_type': data_type,
                        'field_list': field_list,
                        'error_message_fields': "You cannot use same field name twice.",
                    })
        field_name = response['name'][key]
        field_type = response['type'][key]   
        field_required = response['required'][key]              
        f['fields'].append(
            {
                "name": field_name,
                "field_type": field_type,
                "required": field_required
            }
        )
    data_type.fields = f
    data_type.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))       

# DATA TYPE OBJECT    

def new_data_type_object(request, community_name, data_type_name):        
    community = get_object_or_404(Community, name=community_name)
    data_type = get_object_or_404(DataType, name=data_type_name, community=community)
    if data_type.is_archived:
            return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    fields = data_type.fields
    context = {
        'community': community,
        'data_type': data_type,
        'fields': fields
    }
    return render(request, 'vircom/new_data_type_object.html', context) 

def create_data_type_object(request, community_id, data_type_id):
    community = get_object_or_404(Community, pk=community_id)
    data_type = get_object_or_404(DataType, pk=data_type_id)
    fields = data_type.fields
    f = {}
    f['fields'] = []
    for field in fields['fields']:
        if request.POST[field['name']] == "" and field['required'] == "Yes":
            return render(request, 'vircom/new_data_type_object.html', {
            'community': community,
            'data_type': data_type,
            'fields': fields,
            'error_message': "You cannot leave required fields empty.",
        }) 
        elif request.POST[field['name']] == "" and field['required'] == "No":
            f['fields'].append(
                {
                    "name": field['name'],
                    "field_type": field['field_type'],
                    "required": field['required'],
                    "value": "-"
                }
            )
        else:    
            f['fields'].append(
                {
                    "name": field['name'],
                    "field_type": field['field_type'],
                    "required": field['required'],
                    "value": request.POST[field['name']]
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
    data_type_name = post.data_type.name
    data_type = get_object_or_404(DataType, name=data_type_name)
    for field_dt in data_type.fields['fields']:
        checker = False
        for field_post in post.fields['fields']:
            if field_post['name'] == field_dt['name']:
                checker = True
        if checker == False:
            post.fields['fields'].append({
            "name": field_dt['name'],
            "field_type": field_dt['field_type'],
            "required": field_dt['required'],
            "value": "",
        })
    post.save()    
    context = {
        'community': community,
        'post': post,
    }
    return render(request, 'vircom/edit_post.html', context)

def change_post(request, community_id, post_id):
    community = get_object_or_404(Community, pk=community_id)
    post = DataTypeObject.objects.get(pk=post_id)
    #fields = post.fields
    f = {}
    f['fields'] = []
    for field in post.fields['fields']:
        if request.POST[field['name']] == "" or None and field.required == "Yes":
            return render(request, 'vircom/edit_post.html', {
            'community': community,
            'post': post,
            'error_message': "You cannot leave required fields empty.",
        }) 
        f['fields'].append(
            {
                "name": field['name'],
                "field_type": field['field_type'],
                "required": field['required'],
                "value": request.POST[field['name']]
            }
        )
    post.fields = f
    post.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))     

