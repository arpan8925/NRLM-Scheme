from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    # Role choices
    ADMIN = 'admin'
    DISTRICT_EMPLOYEE = 'district_employee'
    BLOCK_EMPLOYEE = 'block_employee'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (DISTRICT_EMPLOYEE, 'District Level Employee'),
        (BLOCK_EMPLOYEE, 'Block Level Employee'),
    ]

    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ADMIN)

    # Location fields
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    block = models.CharField(max_length=100, blank=True, null=True)

    # Using default id as primary key
    id = models.AutoField(primary_key=True) 

    # Manager specific fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def is_admin(self):
        return self.role == self.ADMIN

    def is_district_employee(self):
        return self.role == self.DISTRICT_EMPLOYEE

    def is_block_employee(self):
        return self.role == self.BLOCK_EMPLOYEE

# These models are deprecated and will be removed
# All functionality is now in the User model
