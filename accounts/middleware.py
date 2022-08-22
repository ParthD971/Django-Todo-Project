from django.shortcuts import redirect
from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthAlreadyAssociated


class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):

    def process_exception(self, request, exception):
        if isinstance(exception, AuthAlreadyAssociated):
            url = self.get_redirect_uri(request, exception)
            return redirect(url)
        return super(CustomSocialAuthExceptionMiddleware, self).process_exception(request, exception)
