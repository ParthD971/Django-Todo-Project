from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseBadRequest, JsonResponse


class AnonymousUserRequired(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)


class LoginRequiredForApiMixin(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)
