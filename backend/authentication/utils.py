from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import threading
from datetime import datetime

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Util:
    @staticmethod
    def send_email(data):
        email_body = render_to_string('email.html', {
            'title': data.get('title'),
            'general_message': data.get('general_message'),
            'call_to_action_message': data.get('call_to_action_message'),
            'confirmation_url': data.get('confirmation_url'),
            'button_text': data.get('button_text'),
            'information_message': data.get('information_message'),
            'ignore_message': 'If you don\'t have an account, you can safely ignore this email.',
            'copyright_message': f'© {datetime.now().year} sekurah. All rights reserved.'
        })
        
        # Create the email
        email = EmailMessage(
            subject=data['email_subject'],
            body=email_body,
            to=[data['to_email']]
        )
        # Set the email to HTML content
        email.content_subtype = 'html'
        
        # Start the email thread
        EmailThread(email).start()
