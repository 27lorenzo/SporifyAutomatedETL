import pandas as pd
import requests
import json
from get_access_token import get_access_token

base_url = 'https://api.spotify.com/v1/'


def read_access_token():
    access_token = get_access_token()
    return access_token


def load_session():
    try:
        with open("../session/session.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_audio_features(track_ids, access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    endpoint_audio_features = 'audio-features'
    url = ''.join([base_url, endpoint_audio_features])
    params = {'ids': ','.join(track_ids)}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()['audio_features']
    else:
        print(f"Error fetching audio features: {response.status_code}")
        return None


def get_recommendations(seed_tracks, seed_artists, access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    endpoint_recommendations = 'recommendations'
    url = ''.join([base_url, endpoint_recommendations])
    params = {
        'seed_tracks': seed_tracks,
        'seed_artists': seed_artists,
        'limit': 50
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()['tracks']
    else:
        print(f"Error fetching recommendations: {response.status_code}")
        return None


def main():
    access_token = read_access_token()
    liked_songs_df = pd.read_csv("../dataframes/liked_songs.csv")

    liked_song_ids = liked_songs_df['track_id'].tolist()
    liked_song_artists = liked_songs_df['artist_id'].tolist()
    audio_features = get_audio_features(liked_song_ids, access_token)

    if audio_features:
        seed_tracks = [track_id for track_id in liked_song_ids]
        seed_artists = [artist for artist in liked_song_artists]
        recommendations = get_recommendations(seed_tracks[0:50], seed_artists[0:50], access_token)
        selected_columns = ['name', 'artists']
        if recommendations:
            recommendations_df = pd.DataFrame(recommendations)
            recommendations_df['artists'] = recommendations_df['artists'].apply(
                lambda artists: ', '.join([artist['name'] for artist in artists])
            )
            recommended_songs_df = recommendations_df[selected_columns]
            path_csv = '../dataframes/recommended_songs.csv'
            recommended_songs_df.to_csv(path_csv, index=False)
            print(recommended_songs_df)
        else:
            print("No recommendations could be obtained")


if __name__ == '__main__':
    main()
