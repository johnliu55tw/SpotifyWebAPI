#!/usr/bin/env python3

from flask import Flask, request, send_file, redirect, url_for, abort, jsonify
from os import urandom, getenv
from base64 import b64encode
import sys
import requests as reqts

# Enter your application's client ID and client secret
CLIENT_ID = getenv("CLIENT_ID", None)
CLIENT_SECRET = getenv("CLIENT_SECRET", None)
if CLIENT_ID is None or CLIENT_SECRET is None:
    print("Please set up environment variables 'CLIENT_ID' and 'CLIENT_SECRET")
    sys.exit(-1)


app = Flask(__name__)


def update_token(**kwargs):
    refresh_token = kwargs.get('refresh_token', None)
    if refresh_token:
        reqs_body = {'grant_type': 'refresh_token',
                     'refresh_token': refresh_token}
    else:
        reqs_body = {'grant_type': 'authorization_code',
                     'code': kwargs['code'],
                     'redirect_uri': kwargs['redirect_uri']}

    encoded_credential = b64encode(
            str.encode("{}:{}".format(CLIENT_ID,
                                      CLIENT_SECRET),
                       'ascii')).decode('ascii')

    header = {'Authorization': "Basic " + encoded_credential}
    return reqts.post("https://accounts.spotify.com/api/token",
                      data=reqs_body,
                      headers=header)


@app.route('/')
def index():
    return send_file('public/index.html')


@app.route('/login')
def login():
    state = urandom(16).hex()
    redirect_uri = url_for('callback', _external=True)
    scopes = ["user-library-read",
              "user-modify-playback-state",
              "user-read-playback-state",
              "user-read-currently-playing"]
    resp = redirect("https://accounts.spotify.com/authorize?" +
                    "client_id={}".format(CLIENT_ID) +
                    "&response_type=code" +
                    "&redirect_uri={}".format(redirect_uri) +
                    "&scope={}".format(' '.join(scopes)) +
                    "&state={}".format(state))
    resp.set_cookie('spotify_auth_state', state)
    return resp


@app.route('/callback')
def callback():
    code = request.args.get('code', None)
    state = request.args.get('state', None)
    error = request.args.get('error', None)
    cookie_state = request.cookies.get('spotify_auth_state', None)
    # parameter error is provided
    if error is not None:
        abort(400, "Unable to authorize: {}".format(error))
    print("code:", code, "state:", state)
    print("cookie state:", request.cookies.get('spotify_auth_state'))
    # Verify the state
    if cookie_state is None or cookie_state != state:
        abort(403, "Inconsistent state.")
    # Request for token
    resp = update_token(code=code,
                        redirect_uri=url_for('callback', _external=True))
    if resp.status_code != 200:
        abort(403, "Unable to request token: {}".format(resp.json()))
    resp_json = resp.json()
    print("Scope: ", resp_json['scope'])
    access_token = resp_json['access_token']
    print("Access token:", access_token)
    refresh_token = resp_json['refresh_token']
    # Redirect to index with access token and refresh token
    resp = redirect(url_for('index') + '#' +
                    'access_token={}&'.format(access_token) +
                    'refresh_token={}'.format(refresh_token))
    resp.set_cookie('spotify_auth_state', expires=0)

    return resp


@app.route('/refresh_token')
def refresh_token():
    refresh_token = request.args.get('refresh_token', None)
    resp = update_token(refresh_token=refresh_token)
    if resp.status_code != 200:
        abort(403, "Unable to refresh token: {}".format(resp.json()))

    return jsonify({'access_token': resp.json()['access_token']})


if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)
