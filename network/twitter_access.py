import pathlib

import tweepy
import re
import requests
import json
import sys
import os
import enum

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import game.utils as utils


class AuthState(enum.Enum):
    SUCCESS = 0
    PASSWORD_ERROR = 1
    JSON_ERROR = 2
    LOGIN_PASS_ERROR = 3
    FATAL_ERROR = 4


class Twitter:
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''

    def __init__(self):
        self.auth = tweepy.OAuthHandler(self.CONSUMER_KEY,
                                        self.CONSUMER_SECRET)
        self.auth_url = self.auth.get_authorization_url()

        self.session = requests.session()
        get_resp = self.session.get(self.auth_url)

        re_auth_token = re.compile(
            r'authenticity_token.+?value="([0-9a-z]+?)"', re.M)
        self.auth_token = re_auth_token.search(get_resp.text).group(1)
        self.api = None

    def try_auth_in(self, login, password):
        try:
            with open('access.json') as f:
                data = json.load(f)
        except Exception:
            data = {}

        if not data or login not in data:
            auth_result = self.usual_auth(login, password, data)
        elif login in data:
            auth_result = self.token_auth(login, password, data)
        else:
            return AuthState.FATAL_ERROR

        if auth_result != AuthState.SUCCESS:
            return auth_result

        self.api = tweepy.API(self.auth)
        return AuthState.SUCCESS

    def usual_auth(self, login, password, data):
        post_resp = self.session.post(self.auth_url, data={
            'authenticity_token': self.auth_token,
            'oauth_token': self.auth.request_token['oauth_token'],
            'session[username_or_email]': login,
            'session[password]': password,
            'remember_me': '0'})

        re_verifier = re.compile(r'oauth_verifier=(\w+?)"', re.M)
        res = re_verifier.search(post_resp.text)
        if res is None:
            return AuthState.LOGIN_PASS_ERROR
        verifier = res.group(1)

        try:
            self.auth.get_access_token(verifier)
        except tweepy.TweepError:
            return AuthState.FATAL_ERROR

        self.update_json_data(data, password, login)

        try:
            Twitter.create_json(data, '.')
        except OSError:
            try:
                Twitter.create_json(data, str(pathlib.Path.home()))
            except OSError:
                return AuthState.FATAL_ERROR

        return AuthState.SUCCESS

    def token_auth(self, login, password, data):
        user_data = data[login]
        if not (utils.TwitterUtils.check_pair(user_data[1]) and
                utils.TwitterUtils.check_pair(user_data[2])):
            self.usual_auth(login, password, data)

        decoded_key = utils.TwitterUtils.decode(user_data[1][0], password)
        decoded_secret = utils.TwitterUtils.decode(user_data[2][0],
                                                   password)

        if not (utils.TwitterUtils.check_pair(
                (decoded_key, user_data[0][0])) and
                utils.TwitterUtils.check_pair(
                    (decoded_secret, user_data[0][1]))):
            print('Wrong password!')
            return AuthState.PASSWORD_ERROR

        try:
            self.auth.set_access_token(decoded_key, decoded_secret)
        except tweepy.TweepError:
            return AuthState.FATAL_ERROR

        return AuthState.SUCCESS

    @staticmethod
    def create_json(data, path):
        with open(f'{path}/access.json', 'w') as f:
            json.dump(data, f)

    def update_json_data(self, data, password, login):
        key = self.auth.access_token
        secret = self.auth.access_token_secret
        coded_key = utils.TwitterUtils.code(key, password)
        coded_secret = utils.TwitterUtils.code(secret, password)

        data[login] = ((utils.TwitterUtils.md5_hex(key),
                        utils.TwitterUtils.md5_hex(secret)),
                       (coded_key, utils.TwitterUtils.md5_hex(coded_key)),
                       (
                           coded_secret,
                           utils.TwitterUtils.md5_hex(coded_secret)))

    def send_tweet(self, text):
        if self.api is None:
            raise PermissionError
        while True:
            try:
                self.api.update_status(text)
                return
            except tweepy.error.TweepError:
                text += '~'
