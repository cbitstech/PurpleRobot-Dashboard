from django.contrib.auth.models import *
from django.contrib.gis.db import models

class DashboardUser(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    username = models.CharField(max_length=512, unique=True)

    email = models.EmailField(max_length=512, blank=True, null=True)

    first_name = models.CharField(max_length=512, blank=True, null=True)
    last_name = models.CharField(max_length=512, blank=True, null=True)
    
    affiliation = models.CharField(max_length=512, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def get_short_name(self):
        return self.username

    def get_username(self):
        return self.username
