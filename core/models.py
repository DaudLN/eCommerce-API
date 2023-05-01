from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(verbose_name=_("Email"), unique=True)
