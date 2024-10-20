from django.contrib import admin
from ecommerceApp.models import Contact, Products, Orders, OrderUpdate
# Register your models here.

class Contact_Admin(admin.ModelAdmin):
    list_display=['name','email','desc','phonenumber']
admin.site.register(Contact,Contact_Admin)

class Product_Admin(admin.ModelAdmin):
    list_display=['product_name','category','price']
admin.site.register(Products,Product_Admin)


class Orders_Admin(admin.ModelAdmin):
    list_display = ["order_id","name","email","amountpaid","paymentstatus","state",]
admin.site.register(Orders,Orders_Admin)

class OrderUpdate_Admin(admin.ModelAdmin):
    list_display = ["order_id","delivered","timestamp",]
admin.site.register(OrderUpdate,OrderUpdate_Admin)
