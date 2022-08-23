import re
from .models import User
from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email in User.get_user_emails():
            self.add_error('email', 'This email is already registered.')
        return email

    def clean_password1(self):
        password1 = self.data.get('password1')

        if len(password1) < 5 or len(password1) > 15:
            self.add_error('password1', 'The length of password must be between 5 to 15.')

        if not re.findall('\d', password1):
            self.add_error('password1', 'The password must contain at least 1 digit, 0-9.')
        return password1

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', 'The password is not matching.')
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
            self.add_error('email', 'This email is not registered.')
        elif not User.is_active_user(email=email):
            self.add_error('email', 'The email is not verified.')

        return email

    def clean_password(self):
        password = self.data.get('password')
        email = self.data.get('email')

        query = User.objects.filter(email=email, is_active=True)
        if query.exists() and not query.first().check_password(password):
            self.add_error('password', 'The password is incorrect.')

        return email


class ResendActivationCodeForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.data.get('email')

        if email not in User.get_user_emails():
            self.add_error('email', 'This email is not registered.')
        elif User.is_active_user(email=email):
            self.add_error('email', 'This email is already active.')

        return email


class PasswordResetForm(forms.Form):
    old_password = forms.CharField(required=False)
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.reset_password = kwargs.pop('reset_password', None)
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.data.get('old_password', None)

        if self.reset_password:
            if not old_password:
                self.add_error('old_password', 'Password is Required.')

            if not self.user.check_password(old_password):
                self.add_error('old_password', 'Password is incorrect.')

        return old_password

    def clean_password1(self):
        password1 = self.data.get('password1')

        if len(password1) < 5 or len(password1) > 15:
            self.add_error('password1', 'The length of password must be between 5 to 15.')

        if not re.findall('\d', password1):
            self.add_error('password1', 'The password must contain at least 1 digit, 0-9.')
        return password1

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', 'The password is not matching.')
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
            self.add_error('email', 'This email is not registered.')
        elif User.is_inactive_user(email=email):
            self.add_error('email', 'This email is not verified.')

        return email


class PasswordChangeForm(forms.Form):
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password1(self):
        password1 = self.data.get('password1')

        if len(password1) < 5 or len(password1) > 15:
            self.add_error('password1', 'The length of password must be between 5 to 15.')

        if not re.findall('\d', password1):
            self.add_error('password1', 'The password must contain at least 1 digit, 0-9.')
        return password1

    def clean_password2(self):
        password2 = self.data.get('password2')
        password1 = self.data.get('password1')
        if password1 != password2:
            self.add_error('password2', 'The password is not matching.')
        return password2

    def save(self):
        password = self.data.get('password1')
        self.user.set_password(password)
        self.user.save()