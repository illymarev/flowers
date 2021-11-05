from django.urls import path
from . import views

urlpatterns = [
    path('flowers/', views.flower_list, name='flower_list'),
    path('plants/', views.plant_list, name='plant_list'),
    path('details/<int:id>/', views.product_details, name='product_details'),
    path('flowers/category/<slug:category_slug>/', views.flower_list, name='flowers_by_category'),
    path('plants/category/<slug:category_slug>/', views.plant_list, name='plants_by_category'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]
