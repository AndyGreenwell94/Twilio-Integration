import string

from django.conf import settings

from rest_auth.utils import import_callable

from .sms_backends import BaseBackend as DefaultBackend

# Class used to send sms
# Default choice will rise NotImplemented exception on message send

SMSSBackend = import_callable(
    getattr(
        settings,
        'RESTORE_PASSWORD_SMS_BACKEND',
        DefaultBackend,
    )
)

# Defines field in user model with phone number

PHONE_USER_FIELD = getattr(
    settings,
    'RESTORE_PASSWORD_PHONE_USER_FIELD',
    'phone',
)

# Defines template to use for sms body

MESSAGE_TEMPLATE = getattr(
    settings,
    'RESTORE_PASSWORD_MESSAGE_TEMPLATE',
    'registration/password_reset_subject.txt',
)

# Verification code length, max is 16

CODE_LENGTH = getattr(
    settings,
    'RESTORE_PASSWORD_CODE_LENGTH',
    4
)

# Symbols used to generate key, default is digits

KEY_SYMBOLS = getattr(
    settings,
    'RESTORE_PASSWORD_KEY_SYMBOLS',
    string.digits
)
