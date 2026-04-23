from django.urls import path
from . import views

urlpatterns = [
   path('login/', views.user_login, name='login'),
   path('logout/', views.user_logout, name='logout'),
   path('register/', views.register, name='register'),
   path('add/', views.add_product, name='add_product'),
   path('update-profile/', views.update_profile, name='update_profile'),
]