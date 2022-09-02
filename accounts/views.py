from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from social_django.models import UserSocialAuth

from core.constants import ACCOUNT_REGISTER_SUCCESS, ACCOUNT_ACTIVATION_SUCCESS, ACCOUNT_ACTIVATION_FAILED, \
    ACCOUNT_MODEL_BACKEND, ACCOUNT_LOGIN_SUCCESS, ACCOUNT_LOGIN_FAILED, ACCOUNT_LOGOUT_SUCCESS, \
    ACCOUNT_RESENT_ACTIVATION, ACCOUNT_PASSWORD_RESET_SUCCESS, ACCOUNT_PASSWORD_RESET_LINK_SENT, \
    ACCOUNT_PASSWORD_RESET_INVALID_LINK, ACCOUNT_DEACTIVATION_SUCCESS, ACCOUNT_LOGIN_PAGE, ACCOUNT_REGISTER_PAGE, \
    ACCOUNT_SOCIAL_AUTH_GITHUB, ACCOUNT_SOCIAL_AUTH_TWITTER, ACCOUNT_SOCIAL_AUTH_FACEBOOK, ACCOUNT_SOCIAL_AUTH_GOOGLE, \
    ACCOUNT_SOCIAL_AUTH_MANAGE_PAGE, ACCOUNT_SOCIAL_AUTH_SET_PASSWORD_PAGE
from .forms import RegisterForm, LoginForm, ResendActivationCodeForm, PasswordResetForm, ForgotPasswordForm, \
    PasswordChangeForm
from .mixin import LoginRequiredForApiMixin
from .models import Activation, User
from .utils import send_activation_email, send_reset_password_email
from django.contrib.auth.mixins import LoginRequiredMixin


# Apis
class RegisterApi(View):
    """
    description: This is user register API.
    data:
    {
        [required] email -> string
        [required] password1 -> string
        [required] password2 -> string
    }
    response:
    {
        email: string,
        password1: string,
        password2: string,
        status: string
    }
    permission: Must Be Anonymous user
    """
    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = form.save()
        code = user.get_activation_code()
        send_activation_email(request, user.email, code)

        data = form.cleaned_data
        data['status'] = ACCOUNT_REGISTER_SUCCESS
        return JsonResponse(data)


class ActivateApi(View):
    """
    description: This is user's email activation API.
    request: requires one parameter -> code
    response:
    {
        'message': 'Account activated.'
    }
    :raise: 404 object not found if code is incorrect.
    """
    def get(self, request, code=None, *args, **kwargs):
        act = get_object_or_404(Activation, code=code)

        if not act.is_valid():
            return JsonResponse({'message': ACCOUNT_ACTIVATION_FAILED})

        # Activate profile and Remove the activation record
        act.activate()

        return JsonResponse({'message': ACCOUNT_ACTIVATION_SUCCESS})


class LoginApi(View):
    """
    description: This is user login API.
    data:
    {
        [required] email -> string
        [required] password -> string
    }
    response:
    {
        'message': 'Logged In.'
    }
    permission: Must Be Anonymous user
    """

    # Code to automatically set csrf token in postman
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginApi, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = authenticate(email=email, password=password)
        if user:
            login(request, user, backend=ACCOUNT_MODEL_BACKEND)
            return JsonResponse({'message': ACCOUNT_LOGIN_SUCCESS})
        return JsonResponse({'error': ACCOUNT_LOGIN_FAILED})


class LogoutApi(LoginRequiredForApiMixin, View):
    """
    description: This is user logout API.
    request: requires user object.
    response:
    {
        'message': 'Logged Out.'
    }
    permission: Must Be LoggedIn user
    """
    def get(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'message': ACCOUNT_LOGOUT_SUCCESS})


class ResendActivationCodeApi(View):
    """
    description: This is API for resending activation email.
    request: requires user object.
    data:
    {
        [required] email: string
    }
    response:
    {
        'message': 'Re-sent account activation code.'
    }
    permission: Must Be Anonymous user
    """
    def post(self, request, *args, **kwargs):
        form = ResendActivationCodeForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = User.objects.get(email=form.cleaned_data.get('email'))
        code = user.get_activation_code()
        send_activation_email(request, user.email, code)

        return JsonResponse({'message': ACCOUNT_RESENT_ACTIVATION})


class PasswordResetApi(LoginRequiredForApiMixin, View):
    """
    description: This is API for resetting password.
    data:
    {
        [required] password1: string
        [required] password2: string
    }
    response:
    {
        'message': 'Password reset successful. You must login again.'
    }
    permission: Must Be LoggedIn user
    """
    def post(self, request, *args, **kwargs):
        form = PasswordResetForm(request.POST, user=request.user, reset_password=True)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        form.save(user=request.user)
        logout(request)
        return JsonResponse({'message': ACCOUNT_PASSWORD_RESET_SUCCESS})


class ForgotPasswordApi(View):
    """
    description: This is API for forgot password.
    data:
    {
        [required] email: string
    }
    response:
    {
        'message': 'Link for password reset sent to your email.'
    }
    permission: Must Be Anonymous user
    """
    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)

        if not form.is_valid():
            return JsonResponse(dict(form.errors.items()))

        user = User.objects.get(email=form.cleaned_data.get('email'))
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        send_reset_password_email(self.request, user.email, token, uid)

        return JsonResponse({'message': ACCOUNT_PASSWORD_RESET_LINK_SENT})


class RestorePasswordConfirmApi(View):
    """
    description: This is API for restoring password.
    request: requires uidb64 and token as parameters.
    data:
    {
        [required] password1: string
        [required] password2: string
    }
    response:
    {
        'message': 'Password reset successful.'
    }
    permission: Must Be Anonymous user
    """
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
                return JsonResponse({'message': ACCOUNT_PASSWORD_RESET_SUCCESS})
            return JsonResponse({'error': ACCOUNT_PASSWORD_RESET_INVALID_LINK})
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return JsonResponse({'error': ACCOUNT_PASSWORD_RESET_INVALID_LINK})


class DeactivateAccountApi(LoginRequiredForApiMixin, View):
    """
    description: This is API for deactivating/removing user account.
    request: requires user object.
    response:
    {
        'message': 'Account Deactivated.'
    }
    permission: Must Be LoggedIn user
    """
    def get(self, request):
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        return JsonResponse({'message': ACCOUNT_DEACTIVATION_SUCCESS})


# Views
class LoginView(View):
    """
    description: This is user login view.
    GET request will display Login Form in login.html page.
    POST request will make user login if details is valid else login form with error is displayed.
    permission: Must Be Anonymous user
    """
    def get(self, request):
        form = LoginForm()
        return render(request, template_name=ACCOUNT_LOGIN_PAGE, context={'form': form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(email=email, password=password)
            if user:
                login(request, user, backend=ACCOUNT_MODEL_BACKEND)
                return redirect('home')

            messages.error(request, ACCOUNT_LOGIN_FAILED)
        return render(request, template_name=ACCOUNT_LOGIN_PAGE, context={'form': form})


class RegisterView(View):
    """
    description: This is user register view.
    GET request will display Register Form in register.html page.
    POST request will make user registered if details is valid else register
    form with error is displayed.
    permission: Must Be Anonymous user
    """
    def get(self, request):
        form = RegisterForm()
        return render(request, template_name=ACCOUNT_REGISTER_PAGE, context={'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            code = user.get_activation_code()
            send_activation_email(request, user.email, code)
            return redirect('home')
        return render(request, template_name=ACCOUNT_REGISTER_PAGE, context={'form': form})


class LogoutView(LoginRequiredMixin, View):
    """
    description: This is user logout view.
    GET request will log out user and redirects to home page.
    permission: Must Be LoggedIn user
    """
    def get(self, request):
        logout(request)
        return redirect('home')


class SocialAuthManageSetting(LoginRequiredMixin, View):
    """
    description: This is managing users social auths.
    GET request will allow user to add/remove social auth accounts.
    permission: Must Be LoggedIn user
    """
    def get(self, request):
        user = request.user

        try:
            github_login = user.social_auth.get(provider=ACCOUNT_SOCIAL_AUTH_GITHUB)
        except UserSocialAuth.DoesNotExist:
            github_login = None

        try:
            twitter_login = user.social_auth.get(provider=ACCOUNT_SOCIAL_AUTH_TWITTER)
        except UserSocialAuth.DoesNotExist:
            twitter_login = None

        try:
            facebook_login = user.social_auth.get(provider=ACCOUNT_SOCIAL_AUTH_FACEBOOK)
        except UserSocialAuth.DoesNotExist:
            facebook_login = None

        try:
            google_login = user.social_auth.get(provider=ACCOUNT_SOCIAL_AUTH_GOOGLE)
        except UserSocialAuth.DoesNotExist:
            google_login = None

        can_disconnect = (user.social_auth.count() > 1 or user.has_usable_password())

        return render(
            request,
            template_name=ACCOUNT_SOCIAL_AUTH_MANAGE_PAGE,
            context={
                'github_login': github_login,
                'twitter_login': twitter_login,
                'facebook_login': facebook_login,
                'google_login': google_login,
                'can_disconnect': can_disconnect
            }
        )


class SocialAuthSetPassword(LoginRequiredMixin, View):
    """
    description: This is setting password for removing all social auths and setup default user account. 
    GET request will Password Change form.
    POST request will set new password to user account if form is valid, else form with error is displayed.
    permission: Must Be LoggedIn user
    """
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, ACCOUNT_SOCIAL_AUTH_SET_PASSWORD_PAGE, {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            logout(request)
            return redirect('home')
        return render(request, ACCOUNT_SOCIAL_AUTH_SET_PASSWORD_PAGE, {'form': form})

