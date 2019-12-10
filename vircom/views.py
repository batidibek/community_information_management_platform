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

# NEW COMMUNITY    

def new_community(request):    
    return render(request, 'vircom/new_community.html')

def create_community(request):
    name = str(request.POST.get('name', "")).strip()
    description = str(request.POST.get('description', "")).strip()
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
    community = Community(name=name, description=description, pub_date=datetime.datetime.now(),tags=tags_dict)
    if community.name == "" or community.description == "":
        return render(request, 'vircom/new_community.html', {
            'community': community,
            'error_message': "Name and Description fields cannot be empty.",
        })
    else:
        fields = {}
        fields['fields'] = [{
                "name": "Title",
                "field_id": "1",
                "field_type": "Text",
                "required": "Yes",
                "enumerated": "No",
                "multi_choice": "off",
                "options": []
            },
            {
                "name": "Description",
                "field_id": "2",
                "field_type": "Long Text",
                "required": "Yes",
                "enumerated": "No",
                "multi_choice": "off",
                "options": []
            }
        ]
        community.save()
        post = DataType (name="Generic Post", community=community, fields=fields)
        post.save()
        return HttpResponseRedirect(reverse('vircom:index'))
    

# COMMUNITY DETAIL    

def community_detail(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    return render(request, 'vircom/community_detail.html', context)

#NEW DATA TYPE        

def new_data_type(request, community_name):        
    community = get_object_or_404(Community, name=community_name)
    context = {
        'community': community,
    }
    return render(request, 'vircom/new_data_type.html', context) 

def create_data_type(request, community_id):
    print(request.POST)
    community = get_object_or_404(Community, pk=community_id)
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    name = str(request.POST.get('title', "")).strip()
    print(name)
    data_type = DataType(name=name, community=community, fields={})
    field_list = data_type.fields
    f = {}
    f['fields'] = []
    response = dict(request.POST.lists())
    data_type_list = DataType.objects.filter(community=community, is_archived=False)
    for dt in data_type_list:
        if dt.name == name and dt.name != data_type.name:
            return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message': "There is a data type called " + name + " in this community.",
        })
    if data_type.name == "":
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message': "Title field cannot be empty.",
        }) 
    else:
        data_type.name = name
    if request.POST.get('name') == None:
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message_fields': "You need to add at least one field.",
        })    
    for key in range(len(response['name'])):
        if response['name'][key].strip() == "":
            return render(request, 'vircom/new_data_type.html', {
                'community': community,
                'data_type': data_type,
                'field_list': field_list,
                'error_message_fields': "Field Name cannot be empty.",
            }) 
        else:     
            for field in f['fields']:
                if response['name'][key].strip() == field['name']:
                    return render(request, 'vircom/new_data_type.html', {
                        'community': community,
                        'data_type': data_type,
                        'field_list': field_list,
                        'error_message_fields': "You cannot use same field name twice.",
                    })
        field_id = response['fieldId'][key]
        options = []
        field_enumerated = response['enumerated'+field_id][0]
        try:
            multi_choice = response['multiChoice'+field_id][0]
        except KeyError:
            multi_choice = "off"
        if field_enumerated == "Yes":
            options = response['option'+field_id]       
        field_name = response['name'][key].strip()
        field_type = response['type'][key]   
        field_required = response['required'][key]          
        f['fields'].append(
            {
                "name": field_name,
                "field_id": field_id,
                "field_type": field_type,
                "required": field_required,
                "enumerated": field_enumerated,
                "multi_choice": multi_choice,
                "options": options
            }
        )
    data_type.fields = f
    data_type.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))           


#EDIT DATA TYPE

def delete_data_type(request, community_id, data_type_id):    
    community = get_object_or_404(Community, pk=community_id)
    data_type = DataType.objects.get(pk=data_type_id)
    data_type.is_archived = True
    data_type.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def edit_data_type(request, community_name, data_type_id):  
    community = get_object_or_404(Community, name=community_name)
    data_type = DataType.objects.get(pk=data_type_id)
    field_list = data_type.fields
    field_types = ["Text", "Long Text","Integer","Decimal Number", "Date", "Time", "Image", "Video", "Audio", "Location"]
    field_id = 0
    option = 0
    option_counter = {}
    for field in field_list["fields"]:
        field_id = field["field_id"]
        if field["options"] != []:
            option_counter[field_id] = []
            for key in field["options"]:
                option = option + 1
                option_counter[field_id].append({
                    "count": option,
                    "value": key
                })
    print(option_counter)            
    context = {
        'community': community,
        'data_type': data_type,
        'field_list': field_list,
        'field_types': field_types,
        'field_id': field_id,
        'option': option,
        'option_counter': option_counter
    }
    return render(request, 'vircom/edit_data_type.html', context)

def change_data_type(request, community_id, data_type_id):
    print(request.POST)
    community = get_object_or_404(Community, pk=community_id)
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    name = str(request.POST.get('title', "")).strip()
    print(name)
    data_type = get_object_or_404(DataType, pk=data_type_id)
    field_list = data_type.fields
    f = {}
    f['fields'] = []
    response = dict(request.POST.lists())
    data_type_list = DataType.objects.filter(community=community, is_archived=False)
    for dt in data_type_list:
        if dt.name == name and dt.name != data_type.name:
            return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message': "There is a data type called " + name + " in this community.",
        })
    if data_type.name == "":
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message': "Title field cannot be empty.",
        }) 
    else:
        data_type.name = name
    if request.POST.get('name') == None:
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
            'error_message_fields': "You need to add at least one field.",
        })    
    for key in range(len(response['name'])):
        if response['name'][key].strip() == "":
            return render(request, 'vircom/new_data_type.html', {
                'community': community,
                'data_type': data_type,
                'field_list': field_list,
                'error_message_fields': "Field Name cannot be empty.",
            }) 
        else:     
            for field in f['fields']:
                if response['name'][key].strip() == field['name']:
                    return render(request, 'vircom/new_data_type.html', {
                        'community': community,
                        'data_type': data_type,
                        'field_list': field_list,
                        'error_message_fields': "You cannot use same field name twice.",
                    })
        field_id = response['fieldId'][key]
        options = []
        field_enumerated = response['enumerated'+field_id][0]
        try:
            multi_choice = response['multiChoice'+field_id][0]
        except KeyError:
            multi_choice = "off"
        if field_enumerated == "Yes":
            options = response['option'+field_id]       
        field_name = response['name'][key].strip()
        field_type = response['type'][key]   
        field_required = response['required'][key]          
        f['fields'].append(
            {
                "name": field_name,
                "field_id": field_id,
                "field_type": field_type,
                "required": field_required,
                "enumerated": field_enumerated,
                "multi_choice": multi_choice,
                "options": options
            }
        )
    data_type.fields = f
    data_type.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))       

# NEW DATA TYPE OBJECT    

def new_data_type_object(request, community_name, data_type_id):        
    community = get_object_or_404(Community, name=community_name)
    data_type = get_object_or_404(DataType, pk=data_type_id, community=community)
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
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    data_type = get_object_or_404(DataType, pk=data_type_id)
    print(request.POST)
    dt_fields = data_type.fields
    f = {}
    f['fields'] = []
    for dt_field in dt_fields['fields']:
        value = []
        if dt_field['multi_choice'] == "on":
            for option in dt_field['options']:
                try:
                    option_selected = request.POST[option]
                except KeyError:
                    option_selected = "off"    
                if option_selected == "on":
                    value.append(option)  
            if value == "" and dt_field['required'] == "Yes":
                return render(request, 'vircom/new_data_type_object.html', {
                    'community': community,
                    'data_type': data_type,
                    'fields': dt_fields,
                    'error_message': "You cannot leave required fields empty.",
                })
            else:
                if value == "":
                    value = "-"
                f['fields'].append(
                    {
                        "name": dt_field['name'],
                        "field_id": dt_field['field_id'],
                        "field_type": dt_field['field_type'],
                        "required": dt_field['required'],
                        "enumerated": dt_field['enumerated'],
                        "multi_choice": dt_field['multi_choice'],
                        "options": dt_field['options'],
                        "value": value
                    }
                )         
        elif request.POST[dt_field['name']] == "" and dt_field['required'] == "Yes":
            return render(request, 'vircom/new_data_type_object.html', {
            'community': community,
            'data_type': data_type,
            'fields': dt_fields,
            'error_message': "You cannot leave required fields empty.",
        }) 
        else:
            value = request.POST[dt_field['name']] 
            print(value)   
            if value == "" or value == "[Leave Empty]":
                value = "-"
            print(value)    
            f['fields'].append(
                {
                    "name": dt_field['name'],
                    "field_id": dt_field['field_id'],
                    "field_type": dt_field['field_type'],
                    "required": dt_field['required'],
                    "enumerated": dt_field['enumerated'],
                    "multi_choice": dt_field['multi_choice'],
                    "options": dt_field['options'],
                    "value": value
                }
            )
    data_type_object = DataTypeObject(pub_date=datetime.datetime.now(), community=community, data_type=data_type, fields=f)
    data_type_object.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))   

    # EDIT DATA TYPE OBJECT  

def delete_post(request, community_id, post_id):   
    community = get_object_or_404(Community, pk=community_id)  
    post = DataTypeObject.objects.get(pk=post_id)
    post.delete()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def edit_post(request, community_name, post_id):  
    community = get_object_or_404(Community, name=community_name)
    post = DataTypeObject.objects.get(pk=post_id)
    data_type = post.data_type
    #data_type = get_object_or_404(DataType, name=data_type_name)
    for field_dt in data_type.fields['fields']:
        checker = False
        for field_post in post.fields['fields']:
            if field_post['name'] == field_dt['name']:
                checker = True
        if checker == False:
            post.fields['fields'].append({
            "name": field_dt['name'],
            "field_id": fiedl_dt['field_id'],
            "field_type": field_dt['field_type'],
            "required": field_dt['required'],
            "enumerated": field_dt['enumerated'],
            "multi_choice": field_dt['multi_choice'],
            "options": field_dt['options'],
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
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    post = DataTypeObject.objects.get(pk=post_id)
    data_type = post.data_type
    print(request.POST)
    dt_fields = data_type.fields
    f = {}
    f['fields'] = []
    for dt_field in dt_fields['fields']:
        value = []
        if dt_field['multi_choice'] == "on":
            for option in dt_field['options']:
                try:
                    option_selected = request.POST[option]
                except KeyError:
                    option_selected = "off"    
                if option_selected == "on":
                    value.append(option)  
            if value == "" and dt_field['required'] == "Yes":
                return render(request, 'vircom/new_data_type_object.html', {
                    'community': community,
                    'data_type': data_type,
                    'fields': dt_fields,
                    'error_message': "You cannot leave required fields empty.",
                })
            else:
                if value == "":
                    value = "-"
                f['fields'].append(
                    {
                        "name": dt_field['name'],
                        "field_id": dt_field['field_id'],
                        "field_type": dt_field['field_type'],
                        "required": dt_field['required'],
                        "enumerated": dt_field['enumerated'],
                        "multi_choice": dt_field['multi_choice'],
                        "options": dt_field['options'],
                        "value": value
                    }
                )         
        elif request.POST[dt_field['name']] == "" and dt_field['required'] == "Yes":
            return render(request, 'vircom/new_data_type_object.html', {
            'community': community,
            'data_type': data_type,
            'fields': dt_fields,
            'error_message': "You cannot leave required fields empty.",
        }) 
        else:
            value = request.POST[dt_field['name']] 
            print(value)   
            if value == "" or value == "[Leave Empty]":
                value = "-"
            print(value)    
            f['fields'].append(
                {
                    "name": dt_field['name'],
                    "field_id": dt_field['field_id'],
                    "field_type": dt_field['field_type'],
                    "required": dt_field['required'],
                    "enumerated": dt_field['enumerated'],
                    "multi_choice": dt_field['multi_choice'],
                    "options": dt_field['options'],
                    "value": value
                }
            )
    post.fields = f
    post.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))     

