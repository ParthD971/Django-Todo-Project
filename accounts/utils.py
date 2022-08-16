from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .tasks import send_mail_task


def send_mail(to, template, context):
    html_content = render_to_string(f'accounts/emails/{template}.html', context)
    # send mail using celary
    send_mail_task.delay(context['subject'], html_content, to)


def send_activation_email(request, email, code):
    context = {
        'subject': _('Profile activation'),
        'uri': request.build_absolute_uri(reverse('activate-api', kwargs={'code': code})),
    }
    send_mail(email, 'activate_profile', context)


def send_reset_password_email(request, email, token, uid):
    context = {
        'subject': _('Restore password'),
        'uri': request.build_absolute_uri(
            reverse('restore-password-api', kwargs={'uidb64': uid, 'token': token})),
    }
    send_mail(email, 'restore_password_email', context)
