from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('create-group/<str:group_id>/', views.create_group, name='create-group'),
    path('post-charges/<str:group_id>/', views.post_charge, name='post-charges'),
    path('show-charges/<str:user_phone_num>/', views.show_charges, name='show-charges'),
]