from secrets import choice

from . import app_settings


def generate_verification_key():
    """Generates verification key string
    """
    return ''.join(
        choice(app_settings.KEY_SYMBOLS)
        for i in range(app_settings.CODE_LENGTH)
    )
