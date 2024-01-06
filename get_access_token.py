import requests
from datetime import datetime
import config
import time
import json
import os


token_url = 'https://accounts.spotify.com/api/token'
auth_url = 'http://localhost:8888/authorize'
redirect_uri = 'http://localhost:8888/callback'

c = config.config()
client_id = c.readh('spotify_token', 'client_id') or 'localhost'
client_secret = c.readh('spotify_token', 'client_secret') or 'localhost'


def get_access_token():
    session = load_session()

    if session and 'refresh_token' in session and session['expires_at'] > datetime.now().timestamp():
        print("Using existing session.")
        return session['access_token']
    elif session and 'refresh_token' in session and datetime.now().timestamp() > session['expires_at']:
        print("Access token has expired. Refreshing...")
        return refresh_access_token(session['refresh_token'])

    # If no existing session or expired, perform Authorization Code Flow

    print(f"Please, visit the following link to authorize the application:\n{auth_url}")
    while not os.path.exists("session/authorization_code.txt"):
        time.sleep(1)
    with open("session/authorization_code.txt", "r") as file:
        authorization_code = file.read().strip()

    print(f"Authorization code obtained: {authorization_code}")

    # Get the access token using the authorization code
    token_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret
    }

    token_response = requests.post(token_url, data=token_data)
    token_info = token_response.json()
    session = {
        'access_token': token_info['access_token'],
        'refresh_token': token_info['refresh_token'],
        'expires_at': token_info['expires_in'] + datetime.now().timestamp()
    }

    print(f"New access token: {session['access_token']}")
    print(f"Token expires at: {datetime.fromtimestamp(session['expires_at'])}")

    save_session(session)

    return session['access_token']


def refresh_access_token(refresh_token):
    refresh_data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,

    }
    auth = (client_id, client_secret)
    refresh_response = requests.post(token_url, data=refresh_data, auth=auth)
    refresh_info = refresh_response.json()

    new_session = {
        'access_token': refresh_info['access_token'],
        'refresh_token': refresh_token,
        'expires_at': refresh_info['expires_in'] + datetime.now().timestamp()
    }

    save_session(new_session)

    return new_session['access_token']


def load_session():
    try:
        with open("session/session.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_session(session):
    with open("session/session.json", "w") as file:
        json.dump(session, file)
