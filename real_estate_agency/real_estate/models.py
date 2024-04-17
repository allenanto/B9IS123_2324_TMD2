from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Property(models.Model):
    address = models.CharField(max_length=255)
    property_type = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField()
    availability_status = models.BooleanField(default=True)

    def __str__(self):
        return self.address

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    property_preferences = models.TextField()
    viewing_history = models.ManyToManyField(Property, through='Viewing')

    def __str__(self):
        return self.user.username

class Viewing(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    viewing_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.user.username} - {self.property.address}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.user.username
