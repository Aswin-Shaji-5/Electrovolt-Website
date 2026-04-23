from django.urls import path
from . import views

urlpatterns = [
  
    path('', views.home, name='home'),

    path('add-product/', views.add_product, name='add_product'),

    path('edit-product/<int:id>/', views.edit_product, name='edit_product'),

    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),

    path('cart/', views.cart, name='cart'),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
]

