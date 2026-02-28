from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hello/', views.call_hello, name='call_hello'),
    path('profile/', views.profile, name='profile'),
    path('debug-prefix/', views.debug_prefix, name='debug_prefix'),  # TEMP: remove after debugging
]
