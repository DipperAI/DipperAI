import requests
import time
import hmac
import hashlib
import base64
import random

ACCESS_KEY_ID = ''
ACCESS_KEY_SECRET = ''
ENDPOINT = '1583208943291465.cn-hangzhou.fc.aliyuncs.com'


def sign_request(access_key_id, access_key_secret, method, headers, resource):
    string_to_sign = f"{method}\n{headers.get('accept', '')}\n{headers.get('content-md5', '')}\n{headers.get('content-type', '')}\n{headers.get('date', '')}\nx-acs-signature-method:HMAC-SHA1\nx-acs-signature-nonce:{headers.get('x-acs-signature-nonce', '')}\nx-acs-signature-version:1.0\nx-acs-version:{headers.get('x-acs-version', '')}\n{resource}"
    signature = base64.b64encode(hmac.new(access_key_secret.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1).digest())
    return f"acs {access_key_id}:{signature.decode('utf-8')}"


def list_functions():
    method = 'GET'
    headers = {
        "accept": "application/json",
        'date': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
        'host': ENDPOINT,
        "x-acs-signature-nonce": str(random.randint(1, 10000)),
        "x-acs-signature-method": "HMAC-SHA1",
        "x-acs-signature-version": "1.0",
        "x-acs-version": "2023-03-30",
        "content-type": "application/json",
        "content-md5": ""
    }
    resource = f"/2023-03-30/functions"
    headers['authorization'] = sign_request(ACCESS_KEY_ID, ACCESS_KEY_SECRET, method, headers, resource)
    url = f"https://{ENDPOINT}{resource}"
    response = requests.get(url, headers=headers)
    print(response)

list_functions()