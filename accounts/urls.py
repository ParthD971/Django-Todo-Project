from django.urls import path

from .views import (
    RegisterView,
    ActivateView,
    LoginView,
    LogoutView,
    ResendActivationCodeView,
    PasswordResetView,
    RestorePasswordConfirmView,
    ForgotPasswordView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='password-reset'),
    path('restore-password/<uidb64>/<token>/', RestorePasswordConfirmView.as_view(), name='restore_password_confirm'),

    path('activate/<code>/', ActivateView.as_view(), name='activate'),
    path('resent-activation-code/', ResendActivationCodeView.as_view(), name='resend-activation-code'),
]
