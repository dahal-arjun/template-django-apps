from celery import shared_task
from .utils import Util
from datetime import datetime

@shared_task
def send_verification_email(data):
    """
    Send verification email using the existing Util class
    data should contain:
    - to_email
    - email_subject
    - title
    - general_message
    - call_to_action_message
    - confirmation_url
    - button_text
    - information_message
    """
    print("Sending verification email...")
    print(data)
    Util.send_email(data)

@shared_task
def send_password_reset_email(data):
    """
    Send password reset email using the existing Util class
    data should contain:
    - to_email
    - email_subject
    - title
    - general_message
    - call_to_action_message
    - confirmation_url
    - button_text
    - information_message
    """
    Util.send_email(data)