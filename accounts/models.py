import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @classmethod
    def get_user_emails(cls):
        return User.objects.values_list('email', flat=True)

    @classmethod
    def is_active_user(cls, email):
        return User.objects.filter(email=email, is_active=True).exists()

    @classmethod
    def is_inactive_user(cls, email):
        return User.objects.filter(email=email, is_active=False).exists()

    def get_activation_code(self):
        code = uuid.uuid4()

        act = Activation()
        act.code = code
        act.user = self
        act.save()

        return code

    def __str__(self):
        return self.email


class Activation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=36, unique=True)
    email = models.EmailField(blank=True)

    def activate(self):
        user = self.user
        user.is_active = True
        user.save()

        Activation.objects.filter(user=self.user).delete()
