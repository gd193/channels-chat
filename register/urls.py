from django.urls import path, include
from register import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', include('django.contrib.auth.urls')),
]