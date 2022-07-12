from . import constants
import requests
import json


def generate_auth_url(credentials):
    auth_url = constants.GC_AUTH_URL + '?prompt=consent&access_type=offline&include_granted_scopes=true&' + \
               'response_type=code' + '&scope=' + \
               '+'.join([constants.GC_SCOPE_BASE_URL + scope for scope in constants.GC_SCOPES]) + '&redirect_uri=' + \
               credentials["redirect_url"] + '&client_id=' + credentials["client_id"]
    return auth_url


def get_authorize_token(code, credentials):
    params = {
        "code": code,
        "client_id": credentials["client_id"],
        "redirect_uri": credentials["redirect_url"],
        "client_secret": credentials["client_secret"],
        "grant_type": "authorization_code"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(constants.GC_AUTH_EXCODE_URL, data=params, headers=headers)
    return json.loads(response.content)


def get_refresh_authorize_token(refresh_token, credentials):
    params = {
        "client_id": credentials["client_id"],
        "client_secret": credentials["client_secret"],
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(constants.GC_AUTH_EXCODE_URL, data=params, headers=headers)
    return json.loads(response.content)
