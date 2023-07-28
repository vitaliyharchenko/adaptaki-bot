from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json
from db import database


BASE_URL = 'http://127.0.0.1:8000/'
SECRET_CODE = '228'


async def get_token_from_state(state):
    state_data = await state.get_data()
    user_data = state_data.get("user_data", None)
    token = user_data.get("token", None)
    return token


def api_request(url, token="", data={}, method='GET'):
    full_url = BASE_URL + url
    
    headers = {}

    if token:
        headers['Authorization'] = 'Token ' + token

    if method == 'GET':
        if data:
            query_string = urlencode(data)
            full_url += f"?{query_string}"
            data = query_string.encode('ascii')
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
    url = 'users/telegram'
    data = {"telegram_id": user_id, "secret_code": SECRET_CODE}
    user_data = api_request(url=url, data=data, method='POST')
    return user_data


def get_exam_tree():
    url = 'exam_tree/'
    exam_tree = api_request(url=url)
    return exam_tree


def reg_user(reg_data):
    url = 'users/telegram/reg'
    data = reg_data
    data["secret_code"] = SECRET_CODE
    user_data = api_request(url=url, data=data, method='POST')
    return user_data


def get_random_question(token, exam_tag_id=None):
    url = 'questions/random'
    data = {}
    if exam_tag_id:
        data["exam_tag_id"] = exam_tag_id
    question_data = api_request(url=url, token=token, data=data)
    return question_data
    