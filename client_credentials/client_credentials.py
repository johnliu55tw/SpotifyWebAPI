#!/usr/bin/env python3

import requests
from base64 import b64encode

CLIENT_ID = '{MY CLIENT ID}'.encode('ascii')
CLIENT_SECRET = '{MY CLIENT SECERT}'.encode('ascii')

# Requests access token
reqs_body = {'grant_type': 'client_credentials'}

encoded_cred = b64encode(CLIENT_ID + b':' + CLIENT_SECRET).decode('ascii')

header = {'Authorization': "Basic " + encoded_cred}
resp = requests.post("https://accounts.spotify.com/api/token",
                     data=reqs_body,
                     headers=header)

assert resp.status_code == 200, "Response is not 200: {}-{}".format(resp.status_code, resp.reason)

resp_json = resp.json()
token = resp_json['access_token']
token_type = resp_json['token_type']
expires_in = resp_json['expires_in']

# Use the access token to access the Spotify Web API
# Get a list of new releases
header = {'Authorization': "Bearer " + token}
params = {'limit': 20, 'offset': 0}
resp = requests.get("https://api.spotify.com/v1/browse/new-releases",
                    headers=header,
                    params=params)

assert resp.status_code == 200, "Response is not 200: {}-{}".format(resp.status_code, resp.reason)

obj = resp.json()
for idx, album in enumerate(obj['albums']['items'], 1):
    artists_name = ', '.join([artist['name'] for artist in album['artists']])
    print("{:2d}: {} - {}".format(idx, album['name'], artists_name))
