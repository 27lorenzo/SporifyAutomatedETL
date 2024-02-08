import pandas as pd
import requests
import config
from get_access_token import get_access_token

base_url = 'https://api.spotify.com/v1/'


def send_request(access_token, limit=50, next_url=None):

    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    endpoint_liked_songs = 'me/tracks'
    url = next_url or ''.join([base_url, endpoint_liked_songs])
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


def parse_response_liked_songs(r, liked_songs_df):
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
    artist_ids = []
    track_ids = []

    # Extracting only the relevant bits of data from the json object
    for song in data["items"]:
        track = song.get("track", {})
        track_ids.append(track.get("id", ""))
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["artists"][0]["name"])
        artist_ids.append(song["track"]["artists"][0]["id"])

    # Prepare a dictionary in order to turn it into a pandas dataframe below
    songs_dict = {
        "track_id": track_ids,
        "song_name": song_names,
        "artist_name": artist_names,
        "artist_id": artist_ids
    }
    songs_df = pd.DataFrame(songs_dict, columns=["track_id", "song_name", "artist_name", "artist_id"])
    liked_songs_df = pd.concat([liked_songs_df, songs_df], ignore_index=True)

    print(liked_songs_df.to_string())
    path_csv = 'dataframes/liked_songs.csv'
    liked_songs_df.to_csv(path_csv, index=False)
    return liked_songs_df


def main():
    access_token = get_access_token()
    liked_songs_df = pd.DataFrame(columns=["track_id", "song_name", "artist_name", "artist_id"])
    next_url = None
    limit = 50

    while True:
        response = send_request(access_token, limit=limit, next_url=next_url)

        if response is not None:
            liked_songs_df = parse_response_liked_songs(response, liked_songs_df)

            # Obtaing next URL from JSON response
            next_url = response.json().get("next")
            if not next_url:
                break
        else:
            break

    path_csv = 'dataframes/liked_songs.csv'
    liked_songs_df.to_csv(path_csv, index=False)


if __name__ == '__main__':
    c = config.config()
    client_id = c.readh('spotify_token', 'client_id') or 'localhost'
    client_secret = c.readh('spotify_token', 'client_secret') or 'localhost'

    main()

