import sys
import time
import argparse
import operator

import pymongo

from pyspark import SparkContext
from pyspark.sql import SQLContext

def get_target_users(sqlContext, args):
    sqlContext.sql("CREATE TEMPORARY VIEW tweet_view USING com.stratio.datasource.mongodb OPTIONS (host '{}:{}', database '{}', collection '{}')".format(args.database_ip, args.database_port, args.database_name, args.collection_name))
    target_users = sqlContext.sql("SELECT user.screen_name FROM tweet_view where user.location RLIKE '{}'".format(args.regex)).distinct()
    target_users = [x.screen_name for x in target_users.collect()][0:5]
    #target_users = [x.screen_name for x in target_users.collect()]
    return target_users

def update_user_timeline(target_users):
    from poll.task import pull_timeline
    handlers = {}
    for target_user in target_users:
        handlers[target_user] = pull_timeline.delay(target_user)

    while True:
        if 'PENDING' not in [x.state for x in handlers.values()]:
            break
        else:
            print('Wait 60 seconds...')
            time.sleep(60)

    failed = []
    for key in handlers.keys():
        if handlers[key].state == 'FAILURE':
            failed.append(key)
    if len(failed) != 0:
        raise Exception('Following users failed to update timeline: {}'.format(failed))

def analysize_user_timeline(sqlContext, target_user, args):
    sqlContext.sql("CREATE TEMPORARY VIEW {}_view USING com.stratio.datasource.mongodb OPTIONS (host '{}:{}', database 'timeline', collection '{}')".format(target_user, args.database_ip, args.database_port, target_user))
    texts = sqlContext.sql("SELECT text FROM {}_view".format(target_user))
    # TODO, real analyze
    result = texts.rdd.map(lambda x: len(x)).reduce(operator.add)
    return result

def main():
    parser = argparse.ArgumentParser(description="Poll")
    parser.add_argument("-d", "--debug", action='store_true', default=False,
                        help="Enable debug messages.")
    parser.add_argument("--database_ip", type=str, default='localhost', help="Database IP")
    parser.add_argument("--database_port", type=int, default=27017, help="Database Port")
    parser.add_argument("--database_name", type=str, default='tweets', help="Database Name")
    parser.add_argument("--collection_name", type=str, required=True, help="Collection Name")
    parser.add_argument("--regex", type=str, required=True, help="Regex rule")

    args = parser.parse_args()

    sc = SparkContext("local", "Poll App")
    sqlContext =  SQLContext(sc)

    target_users = get_target_users(sqlContext, args)

    #update_user_timeline(target_users)

    result = analysize_user_timeline(sqlContext, target_users[0], args)
    print(result)

if __name__ == "__main__":
    main()

# spark_submit --packages com.stratio.datasource:spark-mongodb_2.11:0.12.0 spark/application.py --collection_name Trump --regex '[C|c]alifornia'
