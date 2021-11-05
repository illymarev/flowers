from django.urls import path
from . import views

urlpatterns = [
    path('place_order/<int:order_number>/', views.place_order, name='place_order'),
    path('place_order/<int:order_number>/<int:product_id>/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('payments/<int:product_id>/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('track_order/', views.track_order, name='track_order'),
    path('order_details/<email>/<int:order_number>/', views.order_details, name='order_details'),
]
