
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db.models.signals import post_save



class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, is_staff=False, is_active=True, is_admin=False):
        if not phone:
            raise ValueError('users must have a phone number')
        if not password:
            raise ValueError('user must have a password')

        user_obj = self.model(
            phone=phone
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,


        )
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,
            is_admin=True,


        )
        return user


class City(models.Model):
    name = models.CharField(max_length=100)
    state= models.CharField(max_length=100)

    class Meta():
        db_table = "City"


class User(AbstractBaseUser):
    password = None
    phone_regex = RegexValidator( regex   =r'^\+?1?\d{9,14}$', message ="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone       = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    name        = models.CharField(max_length = 20, blank = True, null = True)
    first_login = models.BooleanField(default=False)
    active      = models.BooleanField(default=True)
    staff       = models.BooleanField(default=False)
    admin       = models.BooleanField(default=False)
    timestamp   = models.DateTimeField(auto_now_add=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE,null=True, blank=True)


    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @classmethod
    def create(cls,phone):
        rec=cls(phone=phone)
        rec.save()
        return

    def __str__(self):
        return self.phone

    def get_full_name(self):
        if(self.name !=None):
            return self.name
        return self.phone

    def get_short_name(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):

        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active
    
         
class PhoneOTP(models.Model):
    phone_regex = RegexValidator( regex   =r'^\+?1?\d{9,14}$', message ="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone       = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    otp         = models.CharField(max_length = 4, blank = True, null= True)
    count       = models.IntegerField(default = 0, help_text = 'Number of otp sent')
    logged      = models.BooleanField(default = False, help_text = 'If otp verification got successful')

    def __str__(self):
        return str(self.phone) + ' is sent ' + str(self.otp)



class Restaurant(models.Model):
    city=models.ForeignKey(City,on_delete=models.CASCADE,null=True, blank=True)
    name= models.CharField(max_length=100)
    rating=models.CharField(max_length=30,null=True)
    description=models.CharField(max_length=30,null=True)
    landmark=models.CharField(max_length=30,null=True)
    address=models.CharField(max_length=30,null=True)

class Item(models.Model):
    restaurant = models.ForeignKey(Restaurant,on_delete=models.CASCADE,null=True, blank=True)
    name= models.CharField(max_length=100)
    is_active = models.CharField(max_length=30,null=True)
    is_avaliable = models.CharField(max_length=30,null=True)
    price = models.CharField(max_length=30,null=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE,null=True, blank=True)
    city=models.ForeignKey(City,on_delete=models.CASCADE,null=True, blank=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    price= models.DecimalField(max_digits=10, decimal_places=2)
    payment_type=models.CharField(max_length=30,null=False)
    order_status=models.BooleanField(default=False)

    def __str__(self):
        return self.user.phone

class OrderItem(models.Model) :
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE,blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,blank=True, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

class Cart(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE,blank=True, null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True, blank=True)
    quantity = models.IntegerField(default=1)
