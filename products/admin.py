from django.contrib import admin
from .models import Product, SingleFlower, ReviewRating


# Register your models here.
@admin.register(Product)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created', 'is_plant', 'is_sold']
    list_editable = ['is_sold']
    ordering = ['-created']


admin.site.register(ReviewRating)
admin.site.register(SingleFlower)
