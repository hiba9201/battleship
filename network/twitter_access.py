import tweepy
import re
import requests
import json


class Twitter:
    CONSUMER_KEY = 'aO6Z2tez2HJWxBtyVuWvfJxQn'
    CONSUMER_SECRET = 'hYTXyEsV5wItp39R0Ex9x5iVOOpmSjTcWJ9BN3lOJmZ1IvUVZt'

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
                text = f.read()
        except FileNotFoundError:
            with open('access.json', 'a'):
                text = '{}'
        data = json.loads(text)
        if not data or login not in data:
            post_resp = self.session.post(self.auth_url, data={
                'authenticity_token': self.auth_token,
                'oauth_token': self.auth.request_token['oauth_token'],
                'session[username_or_email]': login,
                'session[password]': password,
                'remember_me': '0'})

            re_verifier = re.compile(r'oauth_verifier=(\w+?)"', re.M)
            res = re_verifier.search(post_resp.text)
            if res is None:
                return False
            verifier = res.group(1)

            try:
                self.auth.get_access_token(verifier)
            except tweepy.TweepError:
                return False

            data[login] = (self.auth.access_token,
                           self.auth.access_token_secret)
            new_dump = json.dumps(data)
            with open('access.json', 'w') as f:
                f.write(new_dump)
        elif login in data:
            self.auth.set_access_token(data[login][0], data[login][1])
        else:
            return False

        self.api = tweepy.API(self.auth)
        return True

    def send_tweet(self, text):
        if self.api is None:
            raise PermissionError
        try:
            self.api.update_status(text)
        except Exception as tw_error:
            print(tw_error)
