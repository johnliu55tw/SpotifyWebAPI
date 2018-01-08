#!/usr/bin/env python3
import spotipy
import sys
from os import getenv
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = getenv("CLIENT_ID", None)
CLIENT_SECRET = getenv("CLIENT_SECRET", None)
if CLIENT_ID is None or CLIENT_SECRET is None:
    print("Please set up environment variables 'CLIENT_ID' and 'CLIENT_SECRET")
    sys.exit(-1)


cred_manager = SpotifyClientCredentials(client_id=CLIENT_ID,
                                        client_secret=CLIENT_SECRET)

sp = spotipy.Spotify(client_credentials_manager=cred_manager)
paged_albums = sp.new_releases(limit=20, offset=0)['albums']

for idx, album in enumerate(paged_albums['items'], 1):
    artists_name = ', '.join([artist['name'] for artist in album['artists']])
    print("{:2d}: {} - {}".format(idx, album['name'], artists_name))
