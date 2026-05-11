from django.urls import path
from . import views

urlpatterns = [
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-history/', views.order_history, name='order_history'),
    path('track-order/<int:order_id>/', views.track_order, name='track_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('payment-success/', views.payment_success, name='payment_success'),
]