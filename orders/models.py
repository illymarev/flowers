from django.db import models
from products.models import Product
from accounts.models import Account


# Create your models here.
class Payment(models.Model):
    payment_id = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Paid', 'Paid'),
        ('Delivered', 'Delivered'),
    )

    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    first_name = models.CharField(max_length=100, null=True, default=None)
    last_name = models.CharField(max_length=100, null=True, default=None)
    order_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=200)
    receiver_phone = models.CharField(max_length=20, blank=True)
    sender_phone = models.CharField(max_length=20)
    order_note = models.TextField(blank=True)
    order_total = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    city = models.CharField(max_length=20)
    postal = models.CharField(max_length=30)
    address = models.CharField(max_length=100)
    apartment = models.CharField(max_length=50, blank=True)
    expected_delivery = models.CharField(max_length=60, default='TBA')
    actual_delivery = models.CharField(max_length=60, default='TBA')
    wants_emails = models.BooleanField(default=False)
    tax = models.FloatField()
    total_without_tax = models.FloatField(default=0)
    bonus_points_used = models.IntegerField(default=0)
    delivery = models.FloatField()

    def square_total(self):
        return int(self.order_total * 100)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.order_number


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name
