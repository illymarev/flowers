from django.db import models
from categories.models import Category
from django.db.models import Avg, Count
from accounts.models import Account


# Create your models here.
class SingleFlower(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, blank=False)
    times_purchased = models.IntegerField(default=0)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='images')
    is_sold = models.BooleanField(default=False)
    is_plant = models.BooleanField(blank=False)
    created = models.DateTimeField(auto_now=True)  # stands for created and updated dates
    flowers_inside = models.ManyToManyField(SingleFlower, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=None, blank=True)

    def __str__(self):
        return self.name

    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def count_review(self):
        reviews = ReviewRating.objects.filter(product=self).aggregate(count=Count('rating'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count


from orders.models import OrderProduct  # if placed on top, will cause circular import error


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=30, blank=False)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review for {self.product.name} by {self.user.email}'

    def purchase_verified(self):
        order_products = OrderProduct.objects.filter(order__user__email=self.user.email).values_list('product_id',
                                                                                                     flat=True)
        if self.product_id in order_products:
            return True
