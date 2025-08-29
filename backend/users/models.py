# users/models.py
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  
    email = models.EmailField(_("email address"), unique=True)

    # extra fields
    name = models.CharField(_("full name"), max_length=255, null=True, blank=True)
    phone = models.CharField(_("phone"), max_length=20, null=True, blank=True)

    # User flag
    is_customer = models.BooleanField(default=False)
    is_employer = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        role = "Customer" if self.is_customer else "Employer" if self.is_employer else "User"
        return f"{self.email} ({role})"


