import os
import time
import socket
import contextlib

import pymongo
import twitter

@contextlib.contextmanager
def get_twitter_account(db_ip, db_port, timeout=None, sleep=60):
    num = 0
    worker = '{}:{}'.format(socket.gethostname(), os.getpid())
    accounts = pymongo.MongoClient(db_ip, db_port)['meta']['accounts']
    entry = accounts.find_one_and_update({'in_use':False}, {'$inc': {'counts': 1}, '$set': {'in_use': True, 'worker':worker}}, sort=[('counts', pymongo.ASCENDING)])
    while entry is None:
        num += 1
        if (timeout is not None) and (num > timeout):
            raise Exception('Failed to find an idle account after {} tries'.format(num))
        print('No account available. Sleep {} seconds'.format(sleep))
        time.sleep(sleep)
        entry = accounts.find_one_and_update({'in_use':False}, {'$inc': {'counts': 1}, '$set': {'in_use': True, 'worker':worker}}, sort=[('counts', pymongo.ASCENDING)])

    try:
        yield entry
    finally:
        accounts.find_one_and_update({'username':entry['username']}, {'$set': {'in_use': False, 'worker':None}})


class TwitterSource(object):
    def __init__(self, db_ip, db_port, secret):
        self.db_ip = db_ip
        self.db_port = db_port
        self.api = twitter.Twitter(auth=twitter.OAuth(secret['access_token_key'], secret['access_token_secret'], secret['consumer_key'], secret['consumer_secret']))

    def error_handle(self, e):
        if e.e.code == 401:
            print("Fail: {} Unauthorized (tweets of that user are protected)".format(e.e.code))
        elif e.e.code == 429:
            print("Fail: {} API rate limit exceeded".format(e.e.code))
            rls = self.api.application.rate_limit_status()
            reset = rls.rate_limit_reset
            reset = time.asctime(time.localtime(reset))
            delay = int(rls.rate_limit_reset
                        - time.time()) + 5 # avoid race
            print("Interval limit of {} requests reached, next reset on {}: going to sleep for {} secs".format(rls.rate_limit_limit,reset, delay))
            time.sleep(delay)
        elif e.e.code == 404:
            print("Fail: {} This profile does not exist".format(e.e.code))
        elif e.e.code == 502:
            print("Fail: {} Service currently unavailable, retrying...".format(e.e.code))
        else:
            print("Fail: {}\nRetrying...".format(str(e)[:500]))
        time.sleep(3)

    def _fetch_tweets_with_keyword(self, keyword, max_id=None, count=100):
        kwargs = dict(count=count, q=keyword)
        if max_id:
            kwargs['max_id'] = max_id
        return self.api.search.tweets(**kwargs)['statuses']

    def fetch_tweets_with_keyword(self, keyword):
        max_id = None
        self.tweets =  pymongo.MongoClient(self.db_ip, self.db_port)['tweets'][keyword]
        while True:
            try:
                tweets = self._fetch_tweets_with_keyword(keyword, max_id)
            except twitter.TwitterError as e:
                self.error_handle(e)
            else:
                new = 0
                for tweet in tweets:
                    num = self.tweets.find({'id_str':tweet['id_str']}).count()
                    assert(num in [0, 1])
                    if num == 0:
                        self.tweets.insert_one(tweet)
                        new += 1
                num = len(tweets)
                print("Search for {}, get {} tweets, {} are new".format(keyword, num, new))
                if num == 0:
                    break
                max_id = min([x['id'] for x in tweets])-1 # browse backwards

    def _fetch_user_timeline(self, screen_name, max_id=None, count=150):
        kwargs = dict(count=count, include_rts=1, exclude_replies=0, screen_name=screen_name)
        if max_id:
            kwargs['max_id'] = max_id
        tweets = self.api.statuses.user_timeline(**kwargs)
        return tweets

    def fetch_user_timeline(self, screen_name):
        max_id = None
        self.timeline = pymongo.MongoClient(self.db_ip, self.db_port)['timeline'][screen_name]
        while True:
            try:
                tweets = self._fetch_user_timeline(screen_name, max_id)
            except twitter.TwitterError as e:
                self.error_handle(e)
            else:
                new = 0
                for tweet in tweets:
                    num = self.timeline.find({'id_str':tweet['id_str']}).count()
                    assert(num in [0, 1])
                    if num == 0:
                        self.timeline.insert_one(tweet)
                        new += 1
                num = len(tweets)
                print("Search for {}, get {} tweets, {} are new".format(screen_name, num, new))
                if num == 0:
                    break
                max_id = min([x['id'] for x in tweets])-1 # browse backwards
