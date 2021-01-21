from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
# Create your models here.

# def upload_path(instance, filename):
#     return '/'.join(['covers', str(instance.name), filename])

class CustomUser(AbstractUser):
    name = models.CharField(blank=True, max_length=120)
    address = models.CharField(blank=True, max_length=120)
    phone = models.CharField(blank=True, max_length=120)
    bill = ArrayField(JSONField(None), blank=True, default=list)
    
    



class Products(models.Model):
    name = models.CharField(blank=True, max_length=400)
    price = models.CharField(blank=True, max_length=400)
    description = models.CharField(blank=True, max_length=500)
    category = models.CharField(blank=True, max_length=200)
    category_concrete = models.CharField(blank=True, max_length=200)
    date = models.DateField(auto_now_add=True, null=True)
    img = models.ImageField(blank=True, null=True, upload_to='')
    count = models.IntegerField(null=True)
    count_client = models.IntegerField(null=True)
    count_star = models.IntegerField(null=True)
    count_star_people = models.IntegerField(null=True)
    

    def __str__(self):
        return self.name

    