import logging

from django.conf import settings

from twilio.base.exceptions import TwilioRestException
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import ChatGrant
from twilio.rest import Client

__all__ = (
    'TwilioClient',
    'SmsClient',
    'ChatClient',
    'generate_token',
)

logger = logging.getLogger('django')


class TwilioClient(object):
    """Base class with Twilio rest client
    """
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT,
            settings.TWILIO_TOKEN,
        )


class SmsClient(TwilioClient):
    """Twilio SMS creation class
    """
    def __init__(self):
        super().__init__()
        self.from_number = settings.TWILIO_FROM_NUMBER

    def create_message(self, to, body):
        try:
            return self.client.messages.create(
                to=to,
                from_=self.from_number,
                body=body
            )
        except TwilioRestException:
            logger.warning(f"Couldn't send message to {to}")


class ChatClient(TwilioClient):
    """Twilio Chat class for channel creation
    """
    def __init__(self):
        super().__init__()
        self.chat = self.client.chat.services.get(
            settings.TWILIO_DEFAULT_CHAT
        )

    def create_channel(self,
                       friendly_name,
                       unique_name,
                       channel_type='public'):
        """Creates Twilio chat

        Args:
            friendly_name (str): Human readable chat name
            unique_name (str): Unique identifier for chat
            channel_type (str): Public or private identifier

        Returns:
            channel: twilio channel instance

        """
        try:
            return self.chat.channels.create(
                friendly_name=friendly_name,
                unique_name=unique_name,
                type=channel_type,
            )
        except TwilioRestException as e:
            logger.warning(f"Couldn't create channel {friendly_name} : {e}")

    def remove_channel(self, sid=None, unique_name=None) -> bool:
        """Removes Twilio chat by SID or unique name

        If channel does not exists writes log record only

        Args:
            sid (str): Twilio SID of channel
            unique_name (str): unique name

        Returns:
            bool: True if channel was deleted
        """
        assert sid or unique_name, 'SID or unique name are expected'

        try:
            self.chat.channels(sid or unique_name).delete()
            return True

        except TwilioRestException as e:
            logger.warning(
                f'Could not delete channel with {sid or unique_name}. '
                f'Reason: {e}'
            )

        return False

    def add_member(self, sid, member_name):
        """Adds member with ``member_name`` into chat with ``sid``

        Args:
            sid (str): Twilio SID of channel
            member_name (str): username
        """
        try:
            self.chat.channels(sid).members.create(member_name)
        except TwilioRestException as error:
            # user is already a member of chat, simply skip it silently
            # https://www.twilio.com/docs/api/errors/50404
            if error.code == 50404:
                return

            raise error


def generate_token(identity):
    """Generate JWT token for chat authorization

    Token generates on server to grant permission for
    chant.

    More info: https://www.twilio.com/docs/api/rest/access-tokens

    """
    token = AccessToken(
        settings.TWILIO_ACCOUNT,
        settings.TWILIO_API_KEY,
        settings.TWILIO_SECRET,
        identity=identity
    )
    token.add_grant(
        ChatGrant(service_sid=settings.TWILIO_DEFAULT_CHAT)
    )
    return token
