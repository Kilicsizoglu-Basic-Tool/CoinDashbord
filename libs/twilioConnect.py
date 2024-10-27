from twilio.rest import Client


class twilioConnect:
    """
    A class to handle connections and interactions with the Twilio API.

    Attributes:
    ----------
    account_sid : str
        The Account SID for the Twilio account.
    auth_token : str
        The Auth Token for the Twilio account.
    client : Client
        The Twilio client initialized with the account SID and auth token.

    Methods:
    -------
    __init__():
        Initializes the twilioConnect class with account SID and auth token.
    sendSMS(message: str):
        Sends an SMS message using the Twilio API.
    """
    def __init__(self):
        self.account_sid = ''
        self.auth_token = ''
        self.client = Client(self.account_sid, self.auth_token)

    def sendSMS(self, message):
        message = self.client.messages.create(
            to='whatsapp:',
            from_='whatsapp:',
            body=message)
        print(message)
