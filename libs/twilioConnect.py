import twilio
from twilio.rest import Client


class twilioConnect:
    def __init__(self):
        self.account_sid = ''
        self.auth_token = ''
        self.client = Client(self.account_sid, self.auth_token)

    def sendSMS(self, message):
        message = self.client.messages.create(
            to='whatsapp:+905458175996',
            from_='whatsapp:+14155238886',
            body=message)
        print(message)
