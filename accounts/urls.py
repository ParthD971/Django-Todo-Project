from django.urls import path

from .views import (
    RegisterApi,
    ActivateApi,
    LoginApi,
    LogoutApi,
    ResendActivationCodeApi,
    PasswordResetApi,
    RestorePasswordConfirmApi,
    ForgotPasswordApi,
    LoginView,
    RegisterView,
    LogoutView,
    SocialAuthManageSetting,
    SocialAuthSetPassword,
    DeactivateAccountApi,
)

urlpatterns = [
    # Apis
    path('register/', RegisterApi.as_view(), name='register-api'),
    path('login/', LoginApi.as_view(), name='login-api'),
    path('logout/', LogoutApi.as_view(), name='logout-api'),

    path('password-reset/', PasswordResetApi.as_view(), name='password-reset-api'),

    path('forgot-password/', ForgotPasswordApi.as_view(), name='forgot-password-api'),
    path('restore-password/<uidb64>/<token>/', RestorePasswordConfirmApi.as_view(), name='restore-password-api'),

    path('activate/<code>/', ActivateApi.as_view(), name='activate-api'),
    path('resent-activation-code/', ResendActivationCodeApi.as_view(), name='resend-activation-code-api'),

    path('deactivate/', DeactivateAccountApi.as_view(), name='deactivate-api'),

    # Views
    path('settings/', SocialAuthManageSetting.as_view(), name='settings'),
    path('settings/password/', SocialAuthSetPassword.as_view(), name='password'),

    path('login-view/', LoginView.as_view(), name='login'),
    path('register-view/', RegisterView.as_view(), name='register'),
    path('logout-view/', LogoutView.as_view(), name='logout'),
]
