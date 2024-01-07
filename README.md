# SpotifySongsRecommender
This project is a Python-based application that leverages the Spotify API and Flask to create a music recommendation system. The application analyzes the user's liked songs on Spotify and generates a new playlist with recommended songs that share similar characteristics to the liked songs.
## Requirements
- Python 3.9
- Flask 3.0.0
- Spotify API
## How it Works
1. **Authentication:** Users authenticate with their Spotify via Authentication flow (OAuth 2.0) to grant access to their liked songs.
2. **Extract liked songs:** The app reads the user's liked songs and saved them in a csv file.
3. **Generate recommended songs:** The app analyzes audio features using Spotify API and recommends new songs based on these features.
4. **Create new playlist:** A new playlist is generated on the user's Spotify account with the recommended songs.
## Overview
**1. Authenticate to Spotify API:**

In order to use the Spotify API, the authentication flow must be initialized. It uses OAuth 2.0 which is based on access_token, refresh_token and expires_in date. The authentication code and session credentiales are stored in separated files on session folder. For this porpuse, two scripts are required:
  ```
  python spotify_callback_server.py 
  ```
  - Usage: initiate the Flask server to use localhost:8888 as callback url
  ```
  python get_access_token.py 
  ```
  - Usage: script containing all the required functions for authentication flow. This function is called in the following scripts. 

**2. Extract liked songs:**

Once the user has been authenticated, the script reads its liked songs and save them in a new csv file in the dataframes folder.
  ```
  python extract_liked_songs.py 
  ```
**3. Generate recommended songs:**

Based on the saved liked songs CSV file, a list of 50 recommended songs is created using the Spotify API. This list is stored in a CSV file in the dataframes folder.
  ```
  python recommend_songs.py 
  ```
**4. Create new playlist:**

A new playlist is created on the Spotify user's profile, to which all the recommended songs saved in the CSV file are added.

  ```
  python create_playlist.py 
  ```
