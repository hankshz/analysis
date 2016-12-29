#!/usr/bin/python3
#; -*- mode: Python;-*-

import argparse

def main():
    parser = argparse.ArgumentParser(description="Tasks control Tool")
    parser.add_argument("-d", "--debug", action='store_true', default=False,
                        help="Enable debug messages.")

    subparsers = parser.add_subparsers()

    pull_parser = subparsers.add_parser("pull")
    pull_parser_subparsers = pull_parser.add_subparsers()
    
    pull_tweet_parser = pull_parser_subparsers.add_parser("tweet")
    pull_tweet_parser.set_defaults(action='pull_tweet')
    pull_tweet_parser.add_argument("--keyword", type=str, required=True, help="Keyword")
    
    pull_timeline_parser = pull_parser_subparsers.add_parser("timeline")
    pull_timeline_parser.set_defaults(action='pull_timeline')
    pull_timeline_parser.add_argument("--screen_name", type=str, required=True, help="Screen Name")

    args = parser.parse_args()

    if args.action == 'pull_tweet':
        from poll.task import pull_tweets
        pull_tweets.delay(args.keyword)
    elif args.action == 'pull_timeline':
        from poll.task import pull_timeline
        x = pull_timeline.delay(args.screen_name)
    else:
        print('Unsupported action {}'.format(args.action))

if __name__ == "__main__":
    main()
