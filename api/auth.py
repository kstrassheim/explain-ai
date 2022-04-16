from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.urls import path, re_path
from asgiref.sync import sync_to_async

from dotenv import load_dotenv
from os import getenv
import json
import requests
from urllib import parse
from datetime import datetime, timedelta

urls = [] 

def get_access_token_from_request(request):
    post_data = json.loads(request.body.decode("utf-8"))
    access_token = post_data.get("accessToken")
    return access_token

def get_tokens_from_req_auth(req_auth):
    if req_auth.status_code == 200:
        now = datetime.now()
        resp_access_token = parse.parse_qs(req_auth.text)
        access_token = resp_access_token["access_token"][0]
        refresh_token = resp_access_token["refresh_token"][0]
        expires_in = resp_access_token["expires_in"][0]
        refresh_expires_in = resp_access_token["refresh_token_expires_in"][0]
        expires = now + timedelta(seconds=int(expires_in))
        refresh_expires = now + timedelta(seconds=int(refresh_expires_in))
        return access_token, refresh_token, expires, refresh_expires
    else:
        raise PermissionDenied(f"Requesting access token failed")

def get_access_token_by_authcode(authCode):
    load_dotenv()
    pload = {
        'client_id': getenv('WEBAPP_AUTH_CLIENTID', ''),
        'client_secret': getenv('WEBAPP_AUTH_SECRET', ''),
        'code':authCode
        }
    req_access_token = requests.post('https://github.com/login/oauth/access_token',data = pload)
    return get_tokens_from_req_auth(req_access_token);

def get_access_token_by_refresh_token(refresh_token):
    load_dotenv()
    pload = {
        'client_id': getenv('WEBAPP_AUTH_CLIENTID', ''),
        'client_secret': getenv('WEBAPP_AUTH_SECRET', ''),
        'grant_type':'refresh_token',
        'refresh_token':refresh_token
    }
    req_access_token = requests.post('https://github.com/login/oauth/access_token',data = pload)
    return get_tokens_from_req_auth(req_access_token);

def process_authorization(access_token:str):
    if access_token is None: raise PermissionDenied("Access Token not provided")
    headers = {'Authorization': f'token {access_token}'}
    # params = {'state':"open"}
    req_user_data = requests.get("https://api.github.com/user", headers=headers)
    if req_user_data.status_code == 200:
        user_data = req_user_data.json()
        WEBAPP_AUTH_AUTHORIZED_USERS = getenv('WEBAPP_AUTH_AUTHORIZED_USERS', '').split(',')
        if user_data["login"] in WEBAPP_AUTH_AUTHORIZED_USERS:
            return user_data
        else:
            raise PermissionDenied("User has no access to this project")
    else:
        raise PermissionDenied(f"Requesting user data failed")



# Remark the overloading of string parameter over same url
async def post_auth(request):
    if request.method == "POST":
        post_data = json.loads(request.body.decode("utf-8"))
        auth_code = post_data.get("authCode")
        if auth_code is None: raise PermissionDenied("Auth Code not provided")
        access_token, refresh_token, expires, refresh_expires=get_access_token_by_authcode(auth_code)
        user_data = process_authorization(access_token)
        return await sync_to_async(JsonResponse)({'user':user_data, 'accessToken':access_token, 'refreshToken':refresh_token, 'expires':expires.isoformat(), 'refreshExpires': refresh_expires.isoformat()})
       
    else:
        raise Exception(f"Method {request.method} not allowed")
urls+=[path('api/auth', post_auth)]

async def post_auth_refresh(request):
    if request.method == "POST":
        post_data = json.loads(request.body.decode("utf-8"))
        refresh_token = post_data.get("refreshToken")
        if refresh_token is None: raise PermissionDenied("Refresh Token not provided")
        access_token, refresh_token, expires, refresh_expires=get_access_token_by_refresh_token(refresh_token)
        return await sync_to_async(JsonResponse)({'accessToken':access_token, 'refreshToken':refresh_token, 'expires':expires.isoformat(), 'refreshExpires': refresh_expires.isoformat()})
       
    else:
        raise Exception(f"Method {request.method} not allowed")
urls+=[path('api/auth_refresh', post_auth_refresh)]


