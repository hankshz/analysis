import pymongo
from celery import Celery

from poll.source import get_twitter_account
from poll.source import TwitterSource

ip = 'localhost'
port = 27017
app = Celery('tasks', backend='amqp://localhost', broker='amqp://localhost')


@app.task
def pull_tweets(keyword):
    global ip
    global port
    with get_twitter_account(ip, port) as account:
        source = TwitterSource(ip, port, account)
        source.fetch_tweets_with_keyword(keyword)

@app.task
def pull_timeline(screen_name):
    global ip
    global port
    with get_twitter_account(ip, port) as account:
        source = TwitterSource(ip, port, account)
        source.fetch_user_timeline(screen_name)
