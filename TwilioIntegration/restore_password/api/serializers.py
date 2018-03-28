from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from libs.serializers.fields import PhoneFieldSerializer

from .. import app_settings
from ..forms import PasswordResetForm

UserModel = get_user_model()


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for requesting a password reset throug sms
    """
    phone = PhoneFieldSerializer()

    password_reset_form_class = PasswordResetForm

    def validate_phone(self, value):
        """Create PasswordResetForm with the serializer
        """

        self.reset_form =\
            self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        if not UserModel.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                detail=_('The phone number you entered does not exist. '
                         'Make sure to input country code. Please try again.'),
            )

        return value

    def save(self, **kwargs):
        """Perform  form save
        """
        return self.reset_form.save(**kwargs)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    phone = PhoneFieldSerializer()
    key = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        """Validate user existence and and validation key
        """
        try:
            self.user = UserModel._default_manager.get(**{
                app_settings.PHONE_USER_FIELD: attrs['phone']
            })
        except (TypeError,
                ValueError,
                OverflowError,
                UserModel.DoesNotExist):
            raise ValidationError({'key': ['Invalid verification code']})

        self.custom_validation(attrs)
        self.set_password_form = self.set_password_form_class(
            user=self.user,
            data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not self.user.verification_keys.filter(key=attrs['key']).exists():
            raise ValidationError({'key': ['Invalid verification code']})
        return attrs

    def save(self):
        """Save form data and drop user verification keys
        """
        self.set_password_form.save()
        self.user.verification_keys.all().delete()
