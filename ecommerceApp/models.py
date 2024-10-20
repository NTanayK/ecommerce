from django.db import models

# Create your models here.

class Contact(models.Model):
    # contact_id=models.AutoField(primary_key=True)    Django internally has an auto-increment id so no need to define explicitly.
    name=models.CharField(max_length=50)
    email=models.EmailField()
    desc=models.TextField()
    phonenumber=models.IntegerField()



class Products(models.Model):
    product_id=models.AutoField
    product_name=models.CharField(max_length=50)
    category=models.CharField(max_length=50,default="")
    subcategory=models.CharField(max_length=50,default="")
    price=models.IntegerField(default=0)
    desc=models.CharField(max_length=300)


    image = models.ImageField(upload_to='images/images')    # Image Files will be stored inside the images folder of the media folder 

    

class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)       # This is the id of the particular object 
    items_json = models.CharField(max_length=5000)
    amount = models.IntegerField()
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=90)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=200)
    zip_code = models.CharField(max_length=100)
    oid = models.CharField(max_length=150,blank=True)       # This is the id of the payment
    amountpaid = models.CharField(max_length=500,blank=True,null=True)
    paymentstatus = models.CharField(max_length=100,default="",blank=True)
    phone = models.CharField(max_length=100,default="")
    
    

class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order_id = models.IntegerField(default="")
    update_desc = models.CharField(max_length=5000)
    delivered = models.BooleanField(default=False)
    timestamp = models.DateField(auto_now_add=True)
    
    # def __str__(self):
    #     return self.update_desc[0:7] + "..."

    
    
    
    
    
