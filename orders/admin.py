from django.contrib import admin
from .models import Payment, Order, OrderProduct


# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment', 'product', 'product_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'email', 'sender_phone', 'order_total', 'status',
                    'created_at']
    search_fields = ['order_number', 'email', 'phone']
    list_per_page = 20
    inlines = [OrderProductInline]


admin.site.register(Payment)
admin.site.register(OrderProduct)
