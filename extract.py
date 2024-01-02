import pandas as pd
import requests
from datetime import datetime
import datetime
import config
from urllib.parse import urlencode
import time
import os

token_url = 'https://accounts.spotify.com/api/token'
auth_url = 'https://accounts.spotify.com/authorize'
base_url = 'https://api.spotify.com/v1/'
redirect_uri = 'http://localhost:8888/callback'


def get_access_token_credentials():
    # Authentication via Client Credentials
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'user-read-recently-played'
    }
    auth_response = requests.post(auth_url, data=data)
    access_token = auth_response.json().get('access_token')
    return access_token


def get_access_token():
    # Authentication via Authorization Code Flow
    auth_params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': 'user-read-recently-played'
    }

    auth_url_with_params = f"{auth_url}?{urlencode(auth_params)}"
    print(f"Please, visit the following link to authorize the application:\n{auth_url_with_params}")

    # # After the user has authorized the app, enter the authorization code
    # authorization_code = input("Enter the authorization code: ")
    # Wait for the authorization code to be available
    while not os.path.exists("authorization_code.txt"):
        time.sleep(2)

    with open("authorization_code.txt", "r") as file:
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
    access_token = token_response.json().get('access_token')

    return access_token


def send_request(access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

    endpoint = f'me/player/recently-played?limit=50&after={yesterday_unix_timestamp}'
    recently_played_url = ''.join([base_url, endpoint])
    print(recently_played_url)
    r = requests.get(recently_played_url, headers=headers)

    return r


def parse_response(r):
    data = r.json()
    print(data)
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
    print(song_df)
    return song_df


def main():
    access_token = get_access_token()
    response = send_request(access_token)
    parse_response(response)


if __name__ == '__main__':
    c = config.config()
    client_id = c.readh('spotify_token', 'client_id') or 'localhost'
    client_secret = c.readh('spotify_token', 'client_secret') or 'localhost'


    main()

