class BaseBackend(object):
    """Base sms sender backend

    Provide interface to be implemented for any sms backend

    """

    def create_message(self, to: str, body: str):
        """Method should send new messages

            Args:
                to: phone number where to send message
                body: sms text to be sent
        """
        raise NotImplemented(
            'You should implement backend by yourself'
        )
