from django.urls import path
from UserApp import views

urlpatterns = [
    path('api/users/', views.create_user),
    path('api/users/<int:user_id>/', views.get_user),
    path('api/usersup/<int:user_id>/', views.update_user),
    path('api/usersdelete/<int:user_id>/', views.delete_user),
    path('api/posts/', views.create_post),
    path('api/posts/<int:post_id>/', views.post_detail),
    path('api/postsall/', views.post_list),
]
