from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import generate_verification_key


class VerificationKey(models.Model):
    """Model to store verification keys for the user
    """
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name='verification_keys',
        verbose_name=_('User'),
    )
    key = models.CharField(
        max_length=16,
        default=generate_verification_key,
    )

    @classmethod
    def create(cls, user):
        """Create new verification key

        Perform verification key creation and drop previous keys

        """
        cls.objects.filter(user=user).delete()
        verification_key = cls(user=user)
        verification_key.save()
        return verification_key
