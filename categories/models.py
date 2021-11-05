from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(max_length=50, blank=True)
    is_plant = models.BooleanField()

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        if self.is_plant:
            return f'{self.name} (plant)'
        else:
            return self.name
