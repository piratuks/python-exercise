from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField('User Name', max_length=32, unique=True)
    email = models.EmailField('Email address', unique=True)
    first_name = models.CharField('First Name', max_length=255, blank=True,
                                  null=False)
    last_name = models.CharField('Last Name', max_length=255, blank=True,
                                 null=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} - {self.first_name} {self.last_name}"


class Employee(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)


class Restaurant(models.Model):
    restaurantName = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)


class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    class Meta:  # pylint: disable=too-few-public-methods
        unique_together = ('name', 'price', 'currency')


class Menu(models.Model):
    name = models.CharField(max_length=255)
    day = models.IntegerField()
    created = models.DateTimeField(auto_now=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

    class Meta:  # pylint: disable=too-few-public-methods
        unique_together = ('name', 'day', 'restaurant')


class RefMenu(models.Model):
    menuID = models.ForeignKey(Menu, on_delete=models.CASCADE)
    menuItemID = models.ForeignKey(MenuItem, on_delete=models.CASCADE)

    class Meta:  # pylint: disable=too-few-public-methods
        unique_together = ('menuID', 'menuItemID')


class Vote(models.Model):
    count = models.IntegerField()
    day = models.IntegerField()
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    class Meta:  # pylint: disable=too-few-public-methods
        unique_together = (
            'day', 'menu')  # pylint: disable=too-few-public-methods
