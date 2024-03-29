from django.urls import path
from . import views


app_name = 'vircom'
urlpatterns = [
    #VIEWS
    path('', views.index, name='index'),
    path('<str:community_name>/feed', views.community_detail, name='community_detail'),
    path('<str:community_name>/<str:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<str:community_name>/new-data-type', views.new_data_type, name='new_data_type'),
    path('<str:community_name>/new-<str:data_type_id>', views.new_data_type_object, name='new_data_type_object'),
    path('new-community/', views.new_community, name='new_community'),
    path('<str:community_name>/<str:data_type_id>/edit', views.edit_data_type, name='edit_data_type'),
    path('sign-up/', views.sign_up, name='sign_up'),
    path('log-in/', views.log_in, name='log_in'),
    
    #REQUESTS
    path('<str:community_id>/<str:post_id>/delete-post/', views.delete_post, name='delete_post'),
    path('<str:community_id>/<str:post_id>/change-post/', views.change_post, name='change_post'),
    path('<str:community_id>/create-data-type/', views.create_data_type, name='create_data_type'),
    path('<str:community_id>/<str:data_type_id>/create-data-type-object', views.create_data_type_object, name='create_data_type_object'),
    path('create-community/', views.create_community, name='create_community'),
    path('<str:community_id>/<str:data_type_id>/change-data-type', views.change_data_type, name='change_data_type'),
    path('<str:community_id>/<str:data_type_id>/delete-data-type', views.delete_data_type, name='delete_data_type'),
    path('create-user/', views.create_user, name='create_user'),
    path('authenticate_user/', views.authenticate_user, name='authenticate_user'),
    path('log-out/', views.log_out, name='log_out'),
    path('<str:community_id>/join', views.join_community, name='join_community'),
    path('<str:community_id>/unsubscribe', views.unsubscribe_community, name='unsubscribe_community'),
    path('<str:community_id>/<str:data_type_id>/search', views.advanced_search, name='advanced_search'),
    path('community-search/', views.search_community, name='search_community'),
]