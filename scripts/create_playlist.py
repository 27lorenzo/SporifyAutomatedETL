import requests
import csv
from get_access_token import get_access_token
import json
import os
import base64


base_url = 'https://api.spotify.com/v1/'
auth_url = 'http://localhost:8888/authorize'
redirect_uri = 'http://localhost:8888/callback'
playlist_name = 'New fresh weekly songs by Python & Airflow'
playlist_description = 'Playlist created by Spotify API'


def read_access_token():
    access_token = get_access_token()
    return access_token


def load_session():
    try:
        with open("../session/session.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def create_playlist_if_not_exists(access_token):
    endpoint_playlists = 'me/playlists'
    url_playlists = ''.join([base_url, endpoint_playlists])
    headers = {'Authorization': 'Bearer ' + access_token}
    playlists_response = requests.get(url_playlists, headers=headers)
    playlists_data = playlists_response.json()

    # Verify if the playlist already exists
    existing_playlist = None
    for playlist in playlists_data['items']:
        if playlist['name'] == playlist_name:
            existing_playlist = playlist
            print("Playlist already created")
            break

    if existing_playlist:
        # If exists, add the new songs
        playlist_id = existing_playlist['id']
        set_cover_image(access_token, playlist_id)
        add_songs_to_existing_playlist(access_token, playlist_id)

    else:
        # If not, create new playlist
        playlist = create_new_playlist(access_token)
        playlist_id = playlist['id']
        set_cover_image(access_token, playlist_id)
        add_songs_to_existing_playlist(access_token, playlist_id)


def create_new_playlist(access_token):
    endpoint_playlist = 'me/playlists'.format(user_id='31g4b4phqjms5x2rj7s7avkxj4ki')
    url = ''.join([base_url, endpoint_playlist])
    playlist_data = {'name': playlist_name, 'description': playlist_description, 'public': True}

    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=playlist_data)
    playlist_data = response.json()
    if response.status_code == 201:
        print(f"New playlist created: {playlist_data['name']}")
        return playlist_data
    else:
        print(f"Error creating new playlist: {response.status_code}")
        return None


def set_cover_image(access_token, playlist_id):
    endpoint_cover_image = f'playlists/{playlist_id}/images'
    url_cover_image = ''.join([base_url, endpoint_cover_image])

    cover_image_path = '../images/spotify-playlist-cover-image.jpeg'

    try:
        if not os.path.exists(cover_image_path):
            print(f"Error: The image '{cover_image_path}' does not exist.")
            return
        with open(cover_image_path, 'rb') as image_file:
            cover_image = image_file.read()
            base64_image = base64.b64encode(cover_image)
    except Exception as e:
        print(f'Error: {e}')
    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'image/jpeg'}
    response = requests.put(url_cover_image, headers=headers, data=base64_image)

    if response.status_code == 202:
        print('Cover image successfully set.')
    else:
        print('Error setting cover image.')


def add_songs_to_existing_playlist(access_token, playlist_id):
    with open('../dataframes/recommended_songs.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        songs = [row['name'] for row in reader]

    endpoint_add_songs = f'playlists/{playlist_id}/tracks'
    url_add_songs = ''.join([base_url, endpoint_add_songs])

    uris = []  # List of URI songs
    for song_name in songs:
        uri = get_track_uri(access_token, song_name)
        if uri:
            uris.append(uri)

    headers = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    data = {'uris': uris}
    response = requests.post(url_add_songs, headers=headers, json=data)

    if response.status_code == 201:
        print('Songs successfully added to existing playlist.')
    else:
        print('Error adding songs to existing playlist.')


def get_track_uri(access_token, song_name):
    endpoint_search = 'search'
    url_search = ''.join([base_url, endpoint_search])

    params = {
        'q': song_name,
        'type': 'track',
        'limit': 1  # Limit the search to one song
    }

    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(url_search, headers=headers, params=params)
    search_results = response.json()

    if 'tracks' in search_results and 'items' in search_results['tracks'] and search_results['tracks']['items']:
        track_uri = search_results['tracks']['items'][0]['uri']
        return track_uri
    else:
        print(f'Could not find the URI for the song: {song_name}')
        return None


def main():
    access_token = read_access_token()
    create_playlist_if_not_exists(access_token)


if __name__ == '__main__':
    main()
