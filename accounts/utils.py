from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def send_mail(to, template, context):
    html_content = render_to_string(f'accounts/emails/{template}.html', context)

    msg = EmailMessage(context['subject'], html_content, to=[to])
    msg.send()


def send_activation_email(request, email, code):
    context = {
        'subject': _('Profile activation'),
        'uri': request.build_absolute_uri(reverse('activate', kwargs={'code': code})),
    }

    send_mail(email, 'activate_profile', context)


def send_reset_password_email(request, email, token, uid):
    context = {
        'subject': _('Restore password'),
        'uri': request.build_absolute_uri(
            reverse('restore_password_confirm', kwargs={'uidb64': uid, 'token': token})),
    }

    send_mail(email, 'restore_password_email', context)
