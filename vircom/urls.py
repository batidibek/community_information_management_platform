from django.urls import path
from . import views


app_name = 'vircom'
urlpatterns = [
    #VIEWS
    path('', views.index, name='index'),
    path('<str:community_name>/feed', views.community_detail, name='community_detail'),
    path('<str:community_name>/new-post/', views.new_post, name='new_post'),
    path('<str:community_name>/<str:post_id>/edit-post/', views.edit_post, name='edit_post'),
    path('<str:community_name>/new-data-type', views.new_data_type, name='new_data_type'),
    path('<str:community_name>/new-data-type/<str:fields>', views.new_data_type, name='new_data_type'),
    path('<str:community_name>/new-<str:data_type_name>', views.new_data_type_object, name='new_data_type_object'),
    path('new-community/', views.new_community, name='new_community'),
    #path('<str:community_name>/new-field/, views.new_field, name='new_field'),

    #REQUESTS
    path('<str:community_id>/create-post/', views.create_post, name='create_post'),
    path('<str:community_id>/<str:post_id>/delete-post/', views.delete_post, name='delete_post'),
    path('<str:community_id>/<str:post_id>/change-post/', views.change_post, name='change_post'),
    path('<str:community_id>/create-data-type/<str:fields>', views.create_data_type, name='create_data_type'),
    path('<str:community_id>/add-field/<str:fields>', views.add_field, name='add_field'),
    path('<str:community_id>/<str:data_type_id>/create-data-type-object', views.create_data_type_object, name='create_data_type_object'),
    path('create-community/', views.create_community, name='create_community'),
]