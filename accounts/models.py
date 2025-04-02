from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

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
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

class Manager(models.Model):
    user = models.OneToOneField(
        'User',  # Use string reference instead of direct model
        on_delete=models.CASCADE,
        related_name='account_manager'
    )
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    employee_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = 'Account Manager'
        verbose_name_plural = 'Account Managers'

class Employee(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE)  # Use string reference
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True)
    department = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=10, unique=True)
    position = models.CharField(max_length=100)
    hire_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"
