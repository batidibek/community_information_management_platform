from django.urls import path
from . import views


app_name = 'vircom'
urlpatterns = [
    #VIEWS
    path('', views.index, name='index'),
    path('<str:community_name>/feed', views.community_detail, name='community_detail'),
    path('<str:community_name>/<str:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<str:community_name>/new-data-type', views.new_data_type, name='new_data_type'),
    path('<str:community_name>/new-data-type/<str:fields>', views.new_data_type, name='new_data_type'),
    path('<str:community_name>/new-<str:data_type_name>', views.new_data_type_object, name='new_data_type_object'),
    path('new-community/', views.new_community, name='new_community'),
    path('<str:community_name>/<str:data_type_name>/edit', views.edit_data_type, name='edit_data_type'),
    
    #REQUESTS
    path('<str:community_id>/<str:post_id>/delete-post/', views.delete_post, name='delete_post'),
    path('<str:community_id>/<str:post_id>/change-post/', views.change_post, name='change_post'),
    path('<str:community_id>/create-data-type/<str:fields>', views.create_data_type, name='create_data_type'),
    path('<str:community_id>/add-field/<str:fields>', views.add_field, name='add_field'),
    path('<str:community_id>/remove-field/<str:fields>/<str:field_name>', views.remove_field, name='remove_field'),
    path('<str:community_id>/<str:data_type_id>/create-data-type-object', views.create_data_type_object, name='create_data_type_object'),
    path('create-community/', views.create_community, name='create_community'),
    path('<str:community_id>/<str:data_type_id>/change-data-type', views.change_data_type, name='change_data_type'),
    path('<str:community_id>/<str:data_type_id>/delete-data-type', views.delete_data_type, name='delete_data_type'),
]