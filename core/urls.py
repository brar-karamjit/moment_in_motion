from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hello/', views.call_hello, name='call_hello'),
    path('profile/', views.profile, name='profile'),
]
