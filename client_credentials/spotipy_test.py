#!/usr/bin/env python3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = "{MY CLIENT_ID"
CLIENT_SECRET = "{MY CLIENT SECRET}"


cred_manager = SpotifyClientCredentials(client_id=CLIENT_ID,
                                        client_secret=CLIENT_SECRET)

sp = spotipy.Spotify(client_credentials_manager=cred_manager)
paged_albums = sp.new_releases(limit=20, offset=0)['albums']

for idx, album in enumerate(paged_albums['items'], 1):
    artists_name = ', '.join([artist['name'] for artist in album['artists']])
    print("{:2d}: {} - {}".format(idx, album['name'], artists_name))
