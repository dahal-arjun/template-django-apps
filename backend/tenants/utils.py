
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from urllib.parse import urlencode
from tenants.models import Invitation
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site

class Utils:
    @staticmethod
    def generate_invitation_url(request, invitation: Invitation, redirect_url: str, fallback_url: str = None) -> str:
        token = urlsafe_base64_encode(smart_bytes(invitation.token))
        current_site = get_current_site(request=request).domain

        relative_link = reverse('invitation-accept', kwargs={'token': token})
        abs_url = f"http://{current_site}{relative_link}"

        if redirect_url and fallback_url:
            abs_url = f"{abs_url}?{urlencode({'redirect_url': redirect_url})}&{urlencode({'fallback_url': fallback_url})}"
        return abs_url

