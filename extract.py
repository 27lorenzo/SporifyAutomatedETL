import pandas as pd
import requests
from datetime import datetime, timedelta
import config
import time
import json
import os

token_url = 'https://accounts.spotify.com/api/token'
auth_url = 'http://localhost:8888/authorize'
base_url = 'https://api.spotify.com/v1/'
redirect_uri = 'http://localhost:8888/callback'


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

    refresh_response = requests.post(token_url, data=refresh_data)
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


def send_request(access_token, limit=50):

    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    endpoint_rp = f'me/player/recently-played?limit=50&after={yesterday_unix_timestamp}'
    endpoint_ls = 'me/tracks'
    url = ''.join([base_url, endpoint_ls])
    print(f"Request URL: {url}")
    params = {
        'limit': limit
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 401:
        print("Error 401: Unauthorized. Token may be invalid.")
    elif r.status_code == 403:
        print("Error 403: Forbidden. Token may be valid, but lacks necessary permissions.")
    elif r.status_code != 200:
        print(f"Error: {r.status_code}")
    return r


def parse_response_recently_played(r):
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        return None

    try:
        data = r.json()
    except requests.exceptions.JSONDecodeError:
        print("Error decoding JSON")
        return None
    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])

    # Prepare a dictionary in order to turn it into a pandas dataframe below
    song_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "played_at": played_at_list,
        "timestamp": timestamps
    }
    song_df = pd.DataFrame(song_dict, columns=["song_name", "artist_name", "played_at", "timestamp"])
    print(song_df.to_string())
    return song_df


def parse_response_liked_songs(r):
    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        return None

    try:
        data = r.json()
    except requests.exceptions.JSONDecodeError:
        print("Error decoding JSON")
        return None
    song_names = []
    artist_names = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        timestamps.append(song["added_at"])

    # Prepare a dictionary in order to turn it into a pandas dataframe below
    songs_dict = {
        "song_name": song_names,
        "artist_name": artist_names,
        "timestamp": timestamps
    }
    liked_songs_df = pd.DataFrame(songs_dict, columns=["song_name", "artist_name", "timestamp"])
    print(liked_songs_df.to_string())
    return liked_songs_df


def main():
    access_token = get_access_token()
    response = send_request(access_token)
    liked_songs_df = parse_response_liked_songs(response)


if __name__ == '__main__':
    c = config.config()
    client_id = c.readh('spotify_token', 'client_id') or 'localhost'
    client_secret = c.readh('spotify_token', 'client_secret') or 'localhost'

    main()

