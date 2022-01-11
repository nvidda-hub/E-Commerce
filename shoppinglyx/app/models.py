from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.base import Model

# Create your models here.

STATE_CHOICES = (
                    ('Andaman & Nicobar Islands', 'Andaman and Nicobar Isalands'),
                    ('Assam', 'Assam'),
                    ('Bihar', 'Bihar'),
                    ('Rajasthan', 'Rajasthan'),
                    ('Arunachal Pradesh', 'Arunachal Pradesh'),
                    ('UP', 'Utter Pradesh'),
                    ('Delhi', 'Delhi')
                )

class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    locality = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=50)

    def __str__(self):
        return str(self.user)


CATEGORY_CHOICES = (
                    ('L', 'Laptop'),
                    ('M', 'Mobile'),
                    ('TW', 'Top Wear'),
                    ('BW', 'Bottom Wear'),
                    ('Oils', 'Oils'),
                    ('Daily Essentials', 'Daily Essentials'),
                    ('Board Games', 'Board Games'),
                    ('Watch', 'Watch'),
                    ('Headsets', 'Headsets'),
                    ('Camera', 'Camera'),
                    ('Tablet', 'Tablet')
                    )

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    selling_price = models.FloatField()
    discounted_price = models.FloatField()
    description = models.TextField()
    brand = models.CharField(max_length=100)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=25)
    product_image = models.ImageField(upload_to='productimg')

    def __str__(self):
        return str(self.title)


class Cart(models.Model):
    id = models.AutoField(primary_key=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return str(self.id)
    
    @property
    def total_cost(self):
        return self.quantity*self.product.discounted_price

STATUS_CHOICES = (
                    ('Accepted', 'Accepted'),
                    ('Packed','Packed'),
                    ('On The Way','On The Way'),
                    ('Delivered','Delivered'),
                    ('Cancel','Cancel')
                )

class OrderPlaced(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return str(self.id)

    @property
    def total_cost(self):
        return self.quantity*self.product.discounted_price
