# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from .models import Community, DataType, DataTypeObject, MediaFile, VircomUser
from django.http import Http404
from django.urls import reverse
import datetime
import json
import uuid
from django.core import serializers
from django.http import JsonResponse
from django.core.files import File
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import requests

# HOMEPAGE

def index(request):
    community_list = Community.objects.order_by('-pub_date')[:30]
    if not request.user.is_authenticated:
        context = {
            'community_list': community_list,
        }
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context = {
            'community_list': community_list,
            'user': vircom_user
        }
    return render(request, 'vircom/index.html', context)

# NEW COMMUNITY    

def new_community(request):    
    if not request.user.is_authenticated:
        community_list = Community.objects.order_by('-pub_date')[:30]
        return render(request, 'vircom/index.html', {
            'community_list': community_list,
            'error_message': "You need to Log in or Sign up to create new community.",
        })
    else:   
        return render(request, 'vircom/new_community.html')


def create_community(request):
    if not request.user.is_authenticated:
        community_list = Community.objects.order_by('-pub_date')[:30]
        return render(request, 'vircom/index.html', {
            'community_list': community_list,
            'error_message': "You need to Log in or Sign up to create new community.",
        }) 
    name = str(request.POST.get('name', "")).strip()
    description = str(request.POST.get('description', "")).strip()
    try:
        old_community = Community.objects.get(name=name)
    except:
        old_community = None
    if old_community:
        return render(request, 'vircom/new_community.html', {
            'error_message': "There is another community named " + name,
            'description': description
        })
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:index'))
    if "get_tag" in request.POST:
        if name == "":
            return render(request, 'vircom/new_community.html', {
            'error_message': "You need to enter community name to get tag suggestions.",
            'tags': suggested_tag_list,
            'description': description
        })
        else:
            suggested_tags = suggest_tags(name)
            suggested_tag_list = ""
            if suggested_tags:
                for item in suggested_tags["items"]:
                    suggested_tag_list = suggested_tag_list + item["label"] + ","
                suggested_tag_list = suggested_tag_list[:-1]
            return render(request, 'vircom/new_community.html', {
                'community_name': name,
                'tags': suggested_tag_list,
                'description': description
            })
    community = Community(name=name, description=description, pub_date=datetime.datetime.now(), tags={}, user=request.user)
    if community.name == "" or community.description == "" or request.POST['tags'] == "":
        return render(request, 'vircom/new_community.html', {
            'community': community,
            'error_message': "Name, Description or Tag fields cannot be empty.",
            'description': description
        })
    else:
        tags_dict = get_post_tags(request.POST['tags'])
        if tags_dict:
            tags = tags_dict
        else: 
            tags = {}    
        community.tags = tags
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
        post = DataType(name="Generic Post", community=community, fields=fields, user=request.user)
        post.save()
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        vircom_user.joined_communities.append(community.pk)
        vircom_user.save()
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

# GET WIKIDATA TAGS

def suggest_tags(community_name):
    wiki_items = {}
    wiki_items["items"] = get_wiki_data_items(community_name, 10)
    tags = {}
    tags["items"] = []
    if wiki_items["items"] == []:
        return None
    counter = 0
    deleted_keys = []
    for item in wiki_items['items']: 
        if counter != 0:
            for i in range(0,counter):
                print(str(item["label"]).lower() + "    " + str(wiki_items["items"][i]["label"]).lower())
                if str(item["label"]).lower() == str(wiki_items["items"][i]["label"]).lower():
                    print("true")
                    deleted_keys.append(item)
                    break
        counter = counter + 1 
    for key in deleted_keys:
        wiki_items["items"].remove(key)                  
    return wiki_items

def get_wiki_data_items(search_term, limit):
    url = "https://www.wikidata.org/w/api.php"
    params = {
    "action": "wbsearchentities",
    "format": "json",
    "language": "en",
    "limit": limit,
    "search": search_term
    }
    response = requests.get(url=url, params=params)
    data = response.json()
    return data["search"]


# JOIN COMMUNITY        

def join_community(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    context = {
            'user': request.user,
            'community': community,
            'data_type_list':  data_type_list,
            'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:
        context["error_message"] = "You need to Log in or Sign up to join a community."
        return render(request, 'vircom/community_detail.html', context)
    vircom_user = get_object_or_404(VircomUser, user=request.user)
    if community.pk in vircom_user.joined_communities:
        context["joined"] = True
        context["error_message"] = "You are already a member of " + community.name + "."
        return render(request, 'vircom/community_detail.html', context)
    vircom_user.joined_communities.append(community.pk)
    vircom_user.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

# UNSUBSCRIBE COMMUNITY

def unsubscribe_community(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    context = {
            'community': community,
            'data_type_list':  data_type_list,
            'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:    
        return render(request, 'vircom/community_detail.html', context)
    vircom_user = get_object_or_404(VircomUser, user=request.user)
    context["user"] = vircom_user  
    if community.pk not in vircom_user.joined_communities:
        context["error_message"] = "You are not a member of " + community.name + "."
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user.joined_communities.remove(community.pk)
        vircom_user.save()
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

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
    if not request.user.is_authenticated:
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context["user"] = vircom_user
        if community.pk in vircom_user.joined_communities:
            context["joined"] = True
        return render(request, 'vircom/community_detail.html', context)

#NEW DATA TYPE        

def new_data_type(request, community_name):        
    community = get_object_or_404(Community, name=community_name)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:
        context["error_message"] = "You need to Log in or Sign up to create a data type."
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context["user"] = vircom_user
        if community.pk not in vircom_user.joined_communities:
            context["error_message"] = "You need to join " + community.name + " to create a data type."
            return render(request, 'vircom/community_detail.html', context)
    return render(request, 'vircom/new_data_type.html', context) 

def create_data_type(request, community_id):
    community = get_object_or_404(Community, pk=community_id)
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    name = str(request.POST.get('title', "")).strip()
    data_type = DataType(name=name, community=community, fields={})
    field_list = data_type.fields
    context = {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
        }
    if not request.user.is_authenticated:
        context = {
        'community': community,   
        'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
        'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
        'error_message': "You need to Log in or Sign up to join a community."
        }
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        if community.pk not in vircom_user.joined_communities:
            context = {
                'user': vircom_user,
                'community': community,   
                'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
                'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
                'error_message': "You need to join " + community.name + " to create a data type."
            }
            return render(request, 'vircom/community_detail.html', context)
    f = {}
    f['fields'] = []
    response = dict(request.POST.lists())
    data_type_list = DataType.objects.filter(community=community, is_archived=False, user=request.user)
    for dt in data_type_list:
        if dt.name == name and dt.name != data_type.name:
            context["error_message"] = "There is a data type called " + name + " in this community."
            return render(request, 'vircom/new_data_type.html', context)
    if data_type.name == "": 
        context["error_message"] = "Title field cannot be empty."
        return render(request, 'vircom/new_data_type.html', context) 
    else:
        data_type.name = name
    if request.POST.get('name') == None:
        context["error_message_fields"] = "You need to add at least one field."
        return render(request, 'vircom/new_data_type.html', context)    
    for key in range(len(response['name'])):
        if response['name'][key].strip() == "":
            context["error_message_fields"] = "Field Name cannot be empty."
            return render(request, 'vircom/new_data_type.html', context) 
        else:     
            for field in f['fields']:
                if response['name'][key].strip() == field['name']:
                    context["error_message_fields"] = "You cannot use same field name twice."
                    return render(request, 'vircom/new_data_type.html', context)
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
    data_type.user = request.user
    data_type.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))           


#EDIT DATA TYPE

def delete_data_type(request, community_id, data_type_id):    
    community = get_object_or_404(Community, pk=community_id)
    data_type = DataType.objects.get(pk=data_type_id)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:
        context["error_message"] = "You need to Log in or Sign up."
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context["user"] = vircom_user
        if data_type.user != vircom_user.user or data_type.name == "Generic Post" or community.pk not in vircom_user.joined_communities:
            context["error_message"] = "You need to join " + community.name + " again to take action."
            if community.pk in vircom_user.joined_communities:
                context["joined"] = True
                context["error_message"] = "You can only delete types which you created."
            return render(request, 'vircom/community_detail.html', context)
    data_type.is_archived = True
    data_type.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def edit_data_type(request, community_name, data_type_id):  
    community = get_object_or_404(Community, name=community_name)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    data_type = DataType.objects.get(pk=data_type_id)
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:
        context["error_message"] = "You need to Log in or Sign up."
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context["user"] = vircom_user
        if data_type.user != vircom_user.user or data_type.name == "Generic Post" or community.pk not in vircom_user.joined_communities:
            context["error_message"] = "You need to join " + community.name + " again to take action."
            if community.pk in vircom_user.joined_communities:
                context["joined"] = True
                context["error_message"] = "You can only edit data types which you created."
            return render(request, 'vircom/community_detail.html', context)
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
    context = {
            'community': community,
            'data_type': data_type,
            'field_list': field_list,
    }
    if not request.user.is_authenticated:
        context = {
        'community': community,   
        'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
        'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
        'error_message': "You need to Log in or Sign up.",
        }
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        if data_type.user != vircom_user.user or data_type.name == "Generic Post" or community.pk not in vircom_user.joined_communities:
            context = {
                'user': vircom_user,
                'community': community,   
                'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
                'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
                'error_message': "You need to join " + community.name + " again to take action."
            }
            if community.pk in vircom_user.joined_communities:
                context["joined"] = True
                context['error_message'] = "You can only edit data types which you created."
            return render(request, 'vircom/community_detail.html', context)
    f = {}
    f['fields'] = []
    response = dict(request.POST.lists())
    data_type_list = DataType.objects.filter(community=community, is_archived=False)
    for dt in data_type_list:
        if dt.name == name and dt.name != data_type.name:
            context["error_message"] = "There is a data type called " + name + " in this community."
            return render(request, 'vircom/new_data_type.html', context)
    if data_type.name == "":
        context["error_message"] = "Title field cannot be empty."
        return render(request, 'vircom/new_data_type.html', context) 
    else:
        data_type.name = name
    if request.POST.get('name') == None:
        context["error_message_fields"] = "You need to add at least one field."
        return render(request, 'vircom/new_data_type.html', context)    
    for key in range(len(response['name'])):
        if response['name'][key].strip() == "":
            context["error_message_fields"] = "Field Name cannot be empty."
            return render(request, 'vircom/new_data_type.html', context) 
        else:     
            for field in f['fields']:
                if response['name'][key].strip() == field['name']:
                    context["error_message_fields"] = "You cannot use same field name twice."
                    return render(request, 'vircom/new_data_type.html', context)
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
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    data_type = get_object_or_404(DataType, pk=data_type_id, community=community)
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:
        context["error_message"] = "You need to Log in or Sign up."
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context["user"] = vircom_user
        if community.pk not in vircom_user.joined_communities:
            context["error_message"] = "You can only post on the communities which you joined."
            return render(request, 'vircom/community_detail.html', context)
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
    if not request.user.is_authenticated:
        context = {
        'community': community,   
        'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
        'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
        'error_message': "You need to Log in or Sign up."
        }
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        if community.pk not in vircom_user.joined_communities:
            context = {
                'user': vircom_user,
                'community': community,   
                'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
                'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
                'error_message': "You can only post on the communities which you joined."
            }
            return render(request, 'vircom/community_detail.html', context)
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    data_type = get_object_or_404(DataType, pk=data_type_id)
    dt_fields = data_type.fields
    error_context = {
        'community': community,
        'data_type': data_type,
        'fields': dt_fields,
        'error_message': "You cannot leave required fields empty.",
    }
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
                return render(request, 'vircom/new_data_type_object.html', error_context)    
            elif value == "" and dt_field['required'] == "No":
                value = "-" 
        elif dt_field['field_type'] == "Image" or dt_field['field_type'] == "Video" or dt_field['field_type'] == "Audio":
            user_file = ""
            try:
                user_file = request.FILES[dt_field['name']]
            except KeyError:
                user_file = ""
            if user_file == "" and dt_field['required'] == "Yes":
                return render(request, 'vircom/new_data_type_object.html', error_context) 
            elif user_file == "" and dt_field['required'] == "No":
                value = "-"
            else: 
                media_file = MediaFile(upload=user_file, url="")
                media_url = list(media_file.upload.name)
                counter = 0
                for key in media_url:
                    if key == " ":
                        media_url[counter] = "_"
                    counter = counter + 1    
                media_url = ''.join(media_url)    
                media_file.url = media_url
                media_file.save()
                value = "/media/uploads/" + media_file.url
        elif str(request.POST[dt_field['name']]).strip() == "" and dt_field['required'] == "Yes":
            return render(request, 'vircom/new_data_type_object.html', error_context) 
        else:
            value = str(request.POST[dt_field['name']]).strip()
            if value == "" or value == "[Leave Empty]":
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
        tags_dict = get_post_tags(request.POST['tags'])
        if tags_dict:
            tags = tags_dict
        else: 
            tags = {}    
    data_type_object = DataTypeObject(pub_date=datetime.datetime.now(), community=community, data_type=data_type, fields=f, user=request.user, tags=tags)
    data_type_object.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))   

def get_post_tags(tags):
    tags_array  = tags.split(",")
    tags_dict = {}
    tags_dict['tags'] = []
    for tag in tags_array:
        if tag.strip() != "":
            tags_dict['tags'].append({
                "tag": tag.strip()
            })
        else:
            return None
    counter = 0
    for tag in tags_dict['tags']:
        items = get_wiki_data_items(tag["tag"], 1)
        if items != []:
            if "description" not in items[0]:
                items[0]["description"] = items[0]["label"]
            tags_dict['tags'][counter]["qid"] = items[0]["id"]
            tags_dict['tags'][counter]["label"] = items[0]["label"]
            tags_dict['tags'][counter]["description"] = items[0]["description"]
            tags_dict['tags'][counter]["url"] = items[0]["concepturi"]
        else:
            wiki_item = {"id": "-", "label": tag["tag"], "description": "-", "url":"-"}
            tags_dict['tags'][counter]["qid"] = wiki_item["id"]
            tags_dict['tags'][counter]["label"] = wiki_item["label"]
            tags_dict['tags'][counter]["description"] = wiki_item["description"]
            tags_dict['tags'][counter]["url"] = wiki_item["url"]     
        counter = counter + 1
    return tags_dict

    # EDIT DATA TYPE OBJECT  

def delete_post(request, community_id, post_id):   
    community = get_object_or_404(Community, pk=community_id) 
    post = DataTypeObject.objects.get(pk=post_id)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:
        context["error_message"] = "You need to Log in or Sign up."
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context["user"] = vircom_user
        if post.user != vircom_user.user:
            if community.pk in vircom_user.joined_communities:
                context["joined"] = True
            context["error_message"] = "You can only delete your own posts."
            return render(request, 'vircom/community_detail.html', context) 
    post.delete()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def edit_post(request, community_name, post_id):  
    community = get_object_or_404(Community, name=community_name)
    post = DataTypeObject.objects.get(pk=post_id)
    data_type_list = DataType.objects.filter(community=community).order_by('pk')
    data_type_object_list = DataTypeObject.objects.filter(community=community).order_by('-pub_date')
    context = {
        'community': community,
        'data_type_list':  data_type_list,
        'data_type_object_list': data_type_object_list,
    }
    if not request.user.is_authenticated:
        context["error_message"] = "You need to Log in or Sign up."
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        context["user"] = vircom_user
        if post.user != vircom_user.user:
            if community.pk in vircom_user.joined_communities:
                context["joined"] = True
            context["error_message"] = "You can only edit your own posts."
            return render(request, 'vircom/community_detail.html', context) 
    data_type = post.data_type
    for field_dt in data_type.fields['fields']:
        checker = False
        for field_post in post.fields['fields']:
            if field_post['name'] == field_dt['name']:
                checker = True
        if checker == False:
            post.fields['fields'].append({
            "name": field_dt['name'],
            "field_id": field_dt['field_id'],
            "field_type": field_dt['field_type'],
            "required": field_dt['required'],
            "enumerated": field_dt['enumerated'],
            "multi_choice": field_dt['multi_choice'],
            "options": field_dt['options'],
            "value": "",
        })
    post.save()  
    tag_labels = ""  
    if post.tags != {}:
        for tag in post.tags['tags']:
            tag_labels = tag_labels + tag["tag"] + ","
        tag_labels = tag_labels[:-1]
    context = {
        'community': community,
        'post': post,
        'tag_labels': tag_labels
    }
    return render(request, 'vircom/edit_post.html', context)

def change_post(request, community_id, post_id):
    community = get_object_or_404(Community, pk=community_id)
    post = DataTypeObject.objects.get(pk=post_id)
    tag_labels = ""  
    if post.tags != {}:
        for tag in post.tags['tags']:
            tag_labels = tag_labels + tag["tag"] + ","
        tag_labels = tag_labels[:-1]
    if not request.user.is_authenticated:
        context = {
        'community': community,   
        'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
        'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
        'error_message': "You need to Log in or Sign up."
        }
        return render(request, 'vircom/community_detail.html', context)
    else:
        vircom_user = get_object_or_404(VircomUser, user=request.user)
        if post.user != vircom_user.user:
            context = {
                'user': vircom_user,
                'community': community,   
                'data_type_list': DataType.objects.filter(community=community).order_by('pk'),
                'data_type_object_list': DataTypeObject.objects.filter(community=community).order_by('-pub_date'),
                'error_message': "You can only edit your own posts."
            }
            if community.pk in vircom_user.joined_communities:
                context["joined"] = True
            return render(request, 'vircom/community_detail.html', context)
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))
    data_type = post.data_type
    dt_fields = post.fields
    error_context = {
        'community': community,
        'data_type': data_type,
        'fields': dt_fields,
        'error_message': "You cannot leave required fields empty.",
        'tag_labels': tag_labels
    }
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
                return render(request, 'vircom/new_data_type_object.html', error_context)    
            elif value == "" and dt_field['required'] == "No":
                value = "-" 
        elif dt_field['field_type'] == "Image" or dt_field['field_type'] == "Video" or dt_field['field_type'] == "Audio":
            user_file = ""
            try:
                user_file = request.FILES[dt_field['name']]
            except KeyError:
                user_file = ""
            if user_file == "" and dt_field['required'] == "Yes":
                post_url = dt_field["value"][15:]
                media_file_list = MediaFile.objects.filter(url=post_url).order_by("-pk")
                media_file = media_file_list[0]  
                value = "/media/" + str(media_file)
            elif user_file == "" and dt_field['required'] == "No":
                value = "-"
            else: 
                media_file = MediaFile(upload=user_file, url="")
                print(str(media_file))
                media_file.url = "/media/" + str(media_file)
                media_file.save()
                value = media_file.url
        elif str(request.POST[dt_field['name']]).strip() == "" and dt_field['required'] == "Yes":
            return render(request, 'vircom/new_data_type_object.html', error_context) 
        else:
            value = str(request.POST[dt_field['name']]).strip()  
            if value == "" or value == "[Leave Empty]":
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
    tags_dict = get_post_tags(request.POST['tags'])
    if tags_dict:
        tags = tags_dict
    else: 
        tags = {}        
    post.fields = f
    post.tags = tags
    post.save()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))     


#USER

#SIGN UP

def sign_up(request):
    return render(request, 'vircom/sign_up.html')

def create_user(request):
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:index'))
    username = request.POST["username"] 
    email = request.POST["email"]
    password = request.POST["password"]   
    if " " in username:
        return render(request, 'vircom/sign_up.html', {
            'error_message': "You cannot use blank space in username.",
        })
    if username == "" or email == "" or password == "":
        return render(request, 'vircom/sign_up.html', {
            'error_message': "You cannot leave username, mail adress and password fields empty.",
        })
    if len(password) < 8:
        return render(request, 'vircom/sign_up.html', {
            'error_message': "Your password should contain at least 8 characters.",
        })    
    username_checker = True
    try:
        u = User.objects.get(username=username)
    except:
        username_checker = False
    if username_checker:
        return render(request, 'vircom/sign_up.html', {
            'error_message': "This username is already taken.",
        })
    email_checker = True    
    try:
        u = User.objects.get(email=email)
    except:
        email_checker = False
    if email_checker:
        return render(request, 'vircom/sign_up.html', {
            'error_message': "This email adress has an account.",
        })
    user = User.objects.create_user(username=username, email=email, password=password)     
    user.save()
    login(request, user)
    vircom_user = VircomUser(user=user)
    vircom_user.save()
    return HttpResponseRedirect(reverse('vircom:index'))       

#LOGIN

def log_in(request):
   return render(request, 'vircom/login.html')    

def authenticate_user(request):
    if "cancel" in request.POST:
        return HttpResponseRedirect(reverse('vircom:index'))
    user_key = request.POST["user_key"]
    print(user_key)  
    password = request.POST["password"] 
    if user_key == "" or password == "":
        return render(request, 'vircom/login.html', {
            'error_message': "Please provide your username or email adress, and password.",
        })
    username_checker = False
    try:
        u = User.objects.get(username=user_key)
    except:
        username_checker = True
    email_checker = False
    try:
        u = User.objects.get(email=user_key)
        user_key = u.username
    except:
        email_checker = True
    if username_checker and email_checker:
       return render(request, 'vircom/login.html', {
            'error_message': "This username or email adress does not exist.",
        })         
    user = authenticate(request, username=user_key, password=password)    
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('vircom:index'))
    else:
        return render(request, 'vircom/login.html', {
        'error_message': "Invalid password.",
    })     

def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('vircom:index'))    

# ADVANCED SEARCH

def advanced_search(request, community_name, data_type_id):
    community = get_object_or_404(Community, name=community_name)
    data_type = get_object_or_404(Community, pk=data_type_name)
    context = {
        'community': community,
        'data_type': data_type
    }
    return render(request, 'vircom/advanced_search.html', context) 

def make_advanced_search(request, community_id, data_type_id):
    pass
