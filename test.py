import json
import base64
import aiofiles
import asyncio
import requests
from urllib.parse import urlencode

TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'
OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"


def fetch_token():
    params = {
        'grant_type': 'client_credentials',
        'client_id': 'GZtVGiB1275u99yG3w0gW2Tq',
        'client_secret': 'UMd6nsv9LcaEEUfej1S4GglIzktcs0zv'
    }
    post_data = urlencode(params).encode('utf-8')
    req = requests.post(TOKEN_URL, post_data, timeout=10)
    result = json.loads(req.text)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            raise Exception('please ensure has check the ability')
        return result['access_token']
    else:
        raise Exception('please overwrite the correct API_KEY and SECRET_KEY')


def ocr_text(img_path):
    token = fetch_token()
    image_url = OCR_URL + "?access_token=" + token
    with open(img_path, 'rb') as fp:
        file_content = fp.read()

    post_data = urlencode({'image': base64.b64encode(file_content)})
    result = requests.post(image_url, post_data, timeout=10)
    json_data = result.json(object_hook=dict)

    return json_data


z = ocr_text(r'E:\Temp\1111.png')
x = 1

