from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import RegisterForm, LoginForm, ResendActivationCodeForm, PasswordResetForm, ForgotPasswordForm
from .models import Activation, User
from .utils import send_activation_email, send_reset_password_email
from django.contrib.auth.mixins import LoginRequiredMixin


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
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


class ActivateView(View):
    def get(self, request, code=None, *args, **kwargs):
        act = get_object_or_404(Activation, code=code)

        # Activate profile and Remove the activation record
        act.activate()

        return JsonResponse({'message': 'Account activated.'})


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        email = form.cleaned_data.get('email')
        user = get_object_or_404(User, email=email)
        login(request, user)

        return JsonResponse({'message': 'Logged In.'})


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'message': 'Logged Out.'})


@method_decorator(csrf_exempt, name='dispatch')
class ResendActivationCodeView(View):
    def post(self, request, *args, **kwargs):
        form = ResendActivationCodeForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = User.objects.get(email=form.cleaned_data.get('email'))
        code = user.get_activation_code()
        send_activation_email(request, user.email, code)

        return JsonResponse({'message': 'Re-sent account activation code.'})


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = PasswordResetForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        form.save(user=request.user)
        logout(request)
        return JsonResponse({'message': 'Password reset successful. You must login again.'})


@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordView(View):
    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = User.objects.get(email=form.cleaned_data.get('email'))
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        send_reset_password_email(self.request, user.email, token, uid)

        return JsonResponse({'message': 'Link for password reset sent to your email.'})


@method_decorator(csrf_exempt, name='dispatch')
class RestorePasswordConfirmView(View):
    def post(self, request, uidb64=None, token=None, *args, **kwargs):
        return JsonResponse({'message': 'Done'})
