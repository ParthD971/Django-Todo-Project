from django.contrib.auth.password_validation import validate_password

from core.constants import ACCOUNT_ALREADY_EXIST_EMAIL, ACCOUNT_PASSWORD_NOT_MATCHING, ACCOUNT_EMAIL_NOT_REGISTERED, \
    ACCOUNT_EMAIL_NOT_VERIFIED, ACCOUNT_INCORRECT_PASSWORD, ACCOUNT_ALREADY_ACTIVE_EMAIL, ACCOUNT_PASSWORD_REQUIRED
from .models import User
from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(required=True, validators=[validate_password])
    password2 = forms.CharField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email in User.get_user_emails():
            self.add_error('email', ACCOUNT_ALREADY_EXIST_EMAIL)
        return email

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', ACCOUNT_PASSWORD_NOT_MATCHING)
        return password2

    def save(self):
        email = self.data.get('email')
        password = self.data.get('password1')
        user = User.objects.create_user(email=email, password=password)
        user.is_active = False
        user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email not in User.get_user_emails():
            self.add_error('email', ACCOUNT_EMAIL_NOT_REGISTERED)
        elif not User.is_active_user(email=email):
            self.add_error('email', ACCOUNT_EMAIL_NOT_VERIFIED)

        return email

    def clean_password(self):
        password = self.data.get('password')
        email = self.data.get('email')

        query = User.objects.filter(email=email, is_active=True)
        if query.exists() and not query.first().check_password(password):
            self.add_error('password', ACCOUNT_INCORRECT_PASSWORD)

        return password


class ResendActivationCodeForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email not in User.get_user_emails():
            self.add_error('email', ACCOUNT_EMAIL_NOT_REGISTERED)
        elif User.is_active_user(email=email):
            self.add_error('email', ACCOUNT_ALREADY_ACTIVE_EMAIL)

        return email


class PasswordResetForm(forms.Form):
    old_password = forms.CharField(required=False)
    password1 = forms.CharField(required=True, validators=[validate_password])
    password2 = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.reset_password = kwargs.pop('reset_password', None)
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.data.get('old_password')

        if self.reset_password:
            if not old_password:
                self.add_error('old_password', ACCOUNT_PASSWORD_REQUIRED)

            if not self.user.check_password(old_password):
                self.add_error('old_password', ACCOUNT_INCORRECT_PASSWORD)

        return old_password

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', ACCOUNT_PASSWORD_NOT_MATCHING)
        return password2

    def save(self, user):
        password = self.data.get('password1')
        user.set_password(password)
        user.save()
        return user


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email not in User.get_user_emails():
            self.add_error('email', ACCOUNT_EMAIL_NOT_REGISTERED)
        elif User.is_inactive_user(email=email):
            self.add_error('email', ACCOUNT_EMAIL_NOT_VERIFIED)

        return email


class PasswordChangeForm(forms.Form):
    password1 = forms.CharField(required=True, validators=[validate_password])
    password2 = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', ACCOUNT_PASSWORD_NOT_MATCHING)
        return password2

    def save(self):
        password = self.data.get('password1')
        self.user.set_password(password)
        self.user.save()
