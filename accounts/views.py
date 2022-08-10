from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from social_django.models import UserSocialAuth

from .forms import RegisterForm, LoginForm, ResendActivationCodeForm, PasswordResetForm, ForgotPasswordForm, \
    PasswordChangeForm
from .mixin import AnonymousUserRequired, LoginRequiredForApiMixin
from .models import Activation, User
from .utils import send_activation_email, send_reset_password_email
from django.contrib.auth.mixins import LoginRequiredMixin


# Apis
class RegisterApi(AnonymousUserRequired, View):
    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = form.save()
        code = user.get_activation_code()
        send_activation_email(request, user.email, code)

        data = form.cleaned_data
        data['status'] = 'Successfully registered. To activate please verify email.'
        return JsonResponse(data)


class ActivateApi(View):
    def get(self, request, code=None, *args, **kwargs):
        act = get_object_or_404(Activation, code=code)

        # Activate profile and Remove the activation record
        act.activate()

        return JsonResponse({'message': 'Account activated.'})


class LoginApi(AnonymousUserRequired, View):
    # Code to automatically set csrf token in postman
    # @method_decorator(csrf_exempt)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(LoginApi, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        email = form.cleaned_data.get('email')
        user = get_object_or_404(User, email=email)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return JsonResponse({'message': 'Logged In.'})


class LogoutApi(LoginRequiredForApiMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'message': 'Logged Out.'})


class ResendActivationCodeApi(AnonymousUserRequired, View):
    def post(self, request, *args, **kwargs):
        form = ResendActivationCodeForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = User.objects.get(email=form.cleaned_data.get('email'))
        code = user.get_activation_code()
        send_activation_email(request, user.email, code)

        return JsonResponse({'message': 'Re-sent account activation code.'})


class PasswordResetApi(LoginRequiredForApiMixin, View):
    def post(self, request, *args, **kwargs):
        form = PasswordResetForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        form.save(user=request.user)
        logout(request)
        return JsonResponse({'message': 'Password reset successful. You must login again.'})


class ForgotPasswordApi(AnonymousUserRequired, View):
    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = User.objects.get(email=form.cleaned_data.get('email'))
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        send_reset_password_email(self.request, user.email, token, uid)

        return JsonResponse({'message': 'Link for password reset sent to your email.'})


class RestorePasswordConfirmApi(AnonymousUserRequired, View):
    def post(self, request, uidb64=None, token=None, *args, **kwargs):
        form = PasswordResetForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
            is_token_valid = default_token_generator.check_token(user, token)
            if is_token_valid:
                form.save(user=user)
                logout(request)
                return JsonResponse({'message': 'Password reset successful.'})
            return JsonResponse({'error': 'Invalid Link.'})
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return JsonResponse({'error': 'Invalid Link.'})


class DeactivateAccountApi(LoginRequiredForApiMixin, View):
    def get(self, request):
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        return JsonResponse({'message': 'Account Deactivated.'})


# Views
class LoginView(AnonymousUserRequired, View):
    def get(self, request):
        form = LoginForm()
        return render(request, template_name='accounts/login.html', context={'form': form})

    def post(self, request):
        form = LoginForm(request.POST)

        if not form.is_valid():
            return render(request, template_name='accounts/login.html', context={'form': form})

        email = form.cleaned_data.get('email')
        user = get_object_or_404(User, email=email)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return redirect('home')


class RegisterView(AnonymousUserRequired, View):
    def get(self, request):
        form = RegisterForm()
        return render(request, template_name='accounts/register.html', context={'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if not form.is_valid():
            return render(request, template_name='accounts/register.html', context={'form': form})

        user = form.save()
        code = user.get_activation_code()
        send_activation_email(request, user.email, code)

        return redirect('home')


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('home')


class SocialAuthManageSetting(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        try:
            github_login = user.social_auth.get(provider='github')
        except UserSocialAuth.DoesNotExist:
            github_login = None

        try:
            twitter_login = user.social_auth.get(provider='twitter')
        except UserSocialAuth.DoesNotExist:
            twitter_login = None

        try:
            facebook_login = user.social_auth.get(provider='facebook')
        except UserSocialAuth.DoesNotExist:
            facebook_login = None

        try:
            google_login = user.social_auth.get(provider='google-oauth2')
        except UserSocialAuth.DoesNotExist:
            google_login = None

        can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

        return render(request, 'accounts/settings.html', {
            'github_login': github_login,
            'twitter_login': twitter_login,
            'facebook_login': facebook_login,
            'google_login': google_login,
            'can_disconnect': can_disconnect
        })


class SocialAuthSetPassword(LoginRequiredMixin, View):
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'accounts/password.html', {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            logout(request)
            return redirect('home')
        return render(request, 'accounts/password.html', {'form': form})

