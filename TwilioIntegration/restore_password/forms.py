from django import forms
from django.contrib.auth import get_user_model
from django.template import loader

from . import constants as app_const
from . import app_settings
from .models import VerificationKey

UserModel = get_user_model()
sender = app_settings.SMSSBackend()


class PasswordResetForm(forms.Form):
    """Form to validate phone and send verification sms

    Will send validation sms for the given number if corresponding user exists

    """
    phone = forms.RegexField(
        app_const.PHONE_REGEXP,
        max_length=15,
    )

    def send_sms(self, to_phone, context, message_template):
        """Sends sms for user
        """
        body = loader.render_to_string(message_template, context)
        sender.create_message(to=to_phone, body=body)

    def get_users(self, phone):
        """Given an phone, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.

        """
        active_users = UserModel._default_manager.filter(**{
            app_settings.PHONE_USER_FIELD: phone,
            'is_active': True,
        })
        return (u for u in active_users if u.has_usable_password())

    def save(self, template_name=None):
        """Generate ``VerificationKey`` instance

        Generates a one-use only verification key for resetting password and
        sends it to user through sms

        """
        if not template_name:
            template_name = app_settings.MESSAGE_TEMPLATE
        phone = self.cleaned_data['phone']
        for user in self.get_users(phone):
            context = {'key': VerificationKey.create(user).key}
            self.send_sms(
                to_phone=getattr(user, app_settings.PHONE_USER_FIELD),
                context=context,
                message_template=template_name,
            )
