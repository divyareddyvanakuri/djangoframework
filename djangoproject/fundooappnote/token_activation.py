import jwt
import datetime
import time
from django_short_url.views import get_surl
from django_short_url.models import ShortURL
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from djangoproject.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
# from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

def tokenActivation(username):
    payload = {
        'username': username,
        # 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    }
    # time.sleep(32)
    token = jwt.encode(payload, 'SECRET_KEY').decode('utf-8')
    surl = get_surl(str(token))
    z = surl.split("/")
    token = z[2]
    return token

def tokendecode(surl):
    url = ShortURL.objects.get(surl=surl)
    token = url.lurl
    q = jwt.decode(token,'SECRET_KEY')
    print(q['username'])
    return q['username']


def emailservices():
    pass


