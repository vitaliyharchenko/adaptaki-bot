from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json
from db import database


BASE_URL = 'http://127.0.0.1:8000/'
SECRET_CODE = '228'
    

def api_request(url, user_id=None, data={}, method='GET'):
    full_url = BASE_URL + url

    headers = {}

    if user_id:
        user_data = database.get_user(user_id=user_id)
        if user_data:
            token = user_data['token']
            headers['Authorization'] = 'Token ' + token

    if method == 'GET':
        req = Request(full_url, data, headers, method='GET')
    else:
        req = Request(full_url, urlencode(data).encode(), headers, method='POST')

    response = urlopen(req)

    response = json.load(response)
    if not "error" in response:
        return response
    else:
        print(f"Post request error: {response['error']}")
        raise ConnectionRefusedError


def get_user(user_id):
    url = 'users/telegram/'
    data = {"telegram_id": user_id, "secret_code": SECRET_CODE}
    user_data = api_request(url=url, data=data, method='POST')
    return user_data


def reg_user(reg_data):
    url = 'users/telegram/reg'
    data = reg_data
    data["secret_code"] = SECRET_CODE
    user_data = api_request(url=url, data=data, method='POST')
    return user_data


def get_random_question(user_id):
    url = 'questions/random'
    question_data = api_request(url=url, user_id=user_id)
    return question_data
    