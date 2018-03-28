from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_auth.views import PasswordResetConfirmView

from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
)


class PasswordResetView(GenericAPIView):
    """Calls custom PasswordResetForm save method
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": _("Password reset sms has been sent.")},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(PasswordResetConfirmView):
    """Confirms verification key and set new password
    """
    serializer_class = PasswordResetConfirmSerializer
