from django.contrib import admin
from .models import CustomUser, Products
# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'date']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Products, ProductAdmin)

