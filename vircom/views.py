# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from .models import Community, Post
from django.http import Http404
from django.urls import reverse
import datetime


# Create your views here.



def index(request):
    community_list = Community.objects.order_by('-pub_date')[:30]
    #template = loader.get_template('vircom/index.html')
    context = {
        'community_list': community_list,
    }
    return render(request, 'vircom/index.html', context)

def cummunity_detail(request, community_name):
    community = get_object_or_404(Community, name=community_name)
    # try:
    #     community = Community.objects.get(name=community_name)
    # except Community.DoesNotExist:
    #     raise Http404("This community does not exist")
    post_list = Post.objects.filter(community=community)
    context = {
        'community': community,
        'post_list': post_list
    }
    return render(request, 'vircom/community_detail.html', context)

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

def delete_post(request, community_id, post_id):  
    community = get_object_or_404(Community, pk=community_id)      
    post = Post.objects.get(pk=post_id)
    post.delete()
    return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def edit_post(request, community_name, post_id):  
    community = get_object_or_404(Community, name=community_name)
    post = Post.objects.get(pk=post_id)
    context = {
        'community': community,
        'post': post,
    }
    return render(request, 'vircom/edit_post.html', context)

def change_post(request, community_id, post_id):
    community = get_object_or_404(Community, pk=community_id)
    post = Post.objects.get(pk=post_id)
    post.title = request.POST['title']
    post.body = request.POST['body']
    if post.title == "" or post.body == "":
        return render(request, 'vircom/edit_post.html', {
            'community': community,
            'error_message': "Title and Body fields cannot be empty.",
        })
    else:
        post.save()
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))

def new_data_type(request, community_name, data_type_id):        
    community = get_object_or_404(Community, name=community_name)
    if data_type_id == '':
        data_type = DataType(name="", community=community, fields = {})
        data_type.save()
    else:
        data_type = DataType.objects.get(pk=data_type_id)   
    context = {
        'community': community,
        'data_type': data_type,
    }
    return render(request, 'vircom/new_data_type.html', context) 

def create_data_type(request, community_id, data_type_id):
    community = get_object_or_404(Community, pk=community_id)
    data_type = DataType.objects.get(pk=data_type_id)
    data_type.title = request.POST['title']
    if data_type.title == "":
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'error_message': "Title field cannot be empty.",
        })
    elif data_type.fields == {}:  
        return render(request, 'vircom/new_data_type.html', {
            'community': community,
            'error_message': "You need to add at least one custom field.",
        })
    else:
        data_type.save()
        return HttpResponseRedirect(reverse('vircom:community_detail', args=(community.name,)))           

def new_field(request, community_name, data_type_id):
    community = get_object_or_404(Community, name=community_name)
    data_type = get_object_or_404(DataType, id=data_type_id)
    context = {
        'community': community,
        'data_type': data_type,
    }
    #TO DO not complete yet
    return render(request, 'vircom/new_field.html', context)
    

def add_field(request, community_id, data_type_id):
    community = get_object_or_404(Community, pk=community_id)
    data_type = DataType.objects.get(pk=data_type_id)
    #TO DO not complete yet
    return HttpResponseRedirect(reverse('vircom:new_data_type', args=(community.name,)))