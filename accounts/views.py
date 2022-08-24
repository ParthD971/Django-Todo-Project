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
        data['status'] = 'Successfully registered. To activate please verify email.'
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
            return JsonResponse({'message': 'Activation code is expired. you can apply for resend activation code.'})

        # Activate profile and Remove the activation record
        act.activate()

        return JsonResponse({'message': 'Account activated.'})


class LoginApi(AnonymousUserRequired, View):
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
        user = get_object_or_404(User, email=email)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return JsonResponse({'message': 'Logged In.'})


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
        return JsonResponse({'message': 'Logged Out.'})


class ResendActivationCodeApi(AnonymousUserRequired, View):
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

        return JsonResponse({'message': 'Re-sent account activation code.'})


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
        return JsonResponse({'message': 'Password reset successful. You must login again.'})


class ForgotPasswordApi(AnonymousUserRequired, View):
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

        return JsonResponse({'message': 'Link for password reset sent to your email.'})


class RestorePasswordConfirmApi(AnonymousUserRequired, View):
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
                return JsonResponse({'message': 'Password reset successful.'})
            return JsonResponse({'error': 'Invalid Link.'})
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return JsonResponse({'error': 'Invalid Link.'})


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
        return JsonResponse({'message': 'Account Deactivated.'})


# Views
class LoginView(AnonymousUserRequired, View):
    """
    description: This is user login view.
    GET request will display Login Form in login.html page.
    POST request will make user login if details is valid else login form with error is displayed.
    permission: Must Be Anonymous user
    """
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
    """
    description: This is user register view.
    GET request will display Register Form in register.html page.
    POST request will make user registered if details is valid else register
    form with error is displayed.
    permission: Must Be Anonymous user
    """
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
    """
    description: This is setting password for removing all social auths and setup default user account. 
    GET request will Password Change form.
    POST request will set new password to user account if form is valid, else form with error is displayed.
    permission: Must Be LoggedIn user
    """
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

