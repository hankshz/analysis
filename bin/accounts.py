#!/usr/bin/python3
#; -*- mode: Python;-*-

import argparse

import pymongo

class AccountDatabase(object):
    def __init__(self, ip, port):
        print('Connecting to Database {}:{}'.format(ip, port))
        self.accounts = pymongo.MongoClient(ip, port)['meta']['accounts']

    def show(self):
        for account in self.accounts.find({}):
            print(account)

    def insert(self, username, password, consumer_key, consumer_secret, access_token_key, access_token_secret):
        num = self.accounts.find({'username':username}).count()
        assert(num in [0, 1])
        if num == 1:
            print('Account {} already exists'.format(username))
            return
        entry = {
            'username'              :   username,
            'password'              :   password,
            'consumer_key'          :   consumer_key,
            'consumer_secret'       :   consumer_secret,
            'access_token_key'      :   access_token_key,
            'access_token_secret'   :   access_token_secret,
            'worker'                :   None,
            'in_use'                :   False,
            'counts'                :   0,
            'site'                  :   'twitter',
        }
        self.accounts.insert_one(entry)

    def reset(self):
        self.accounts.update_many({}, {'$set': {'in_use':False,'worker':None}})

    def remove(self, username):
        num = self.accounts.delete_many({'username':username}).deleted_count
        assert(num in [0, 1])
        if num == 0:
            print('Account {} did not exist'.format(username))

def main():
    parser = argparse.ArgumentParser(description="Accounts control Tool")
    parser.add_argument("-d", "--debug", action='store_true', default=False,
                        help="Enable debug messages.")
    parser.add_argument("--database_ip", type=str, default='localhost', help="Database IP")
    parser.add_argument("--database_port", type=int, default=27017, help="Database Port")

    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser("list")
    list_parser.set_defaults(action='list')

    reset_parser = subparsers.add_parser("reset")
    reset_parser.set_defaults(action='reset')

    delete_parser = subparsers.add_parser("delete")
    delete_parser.set_defaults(action='delete')
    delete_parser.add_argument("--username", type=str, required=True, help="Username")

    add_parser = subparsers.add_parser("add")
    add_parser.set_defaults(action='add')
    add_parser.add_argument("--username", type=str, required=True, help="Username")
    add_parser.add_argument("--password", type=str, help="Password", default=None)
    add_parser.add_argument("--consumer_key", type=str, required=True, help="Consumer Key")
    add_parser.add_argument("--consumer_secret", type=str, required=True, help="Consumer Secret")
    add_parser.add_argument("--access_token_key", type=str, required=True, help="Access Token Key")
    add_parser.add_argument("--access_token_secret", type=str, required=True, help="Access Token Secret")

    args = parser.parse_args()

    db = AccountDatabase(args.database_ip, args.database_port)
    if args.action == 'list':
        db.show()
    elif args.action == 'reset':
        db.reset()
    elif args.action == 'add':
        db.insert(args.username, args.password, args.consumer_key, args.consumer_secret, args.access_token_key, args.access_token_secret)
    elif args.action == 'delete':
        db.remove(args.username)
    else:
        print('Unsupported action {}'.format(args.action))

if __name__ == "__main__":
    main()

# ./accounts.py add --username dongbo1 --consumer_key ygUM7CVN4kfoAyp29i4XMwzJw --consumer_secret 6fMEDdeQKOE31KZP3sCfI2boWV6aotF2AaumDNG4llcu7FGK95 --access_token_key 720293239924731905-bF0JO1QYI3CKIdrIhITR3IXfaMVfrKW --access_token_secret bm5W5W04YT8kQRfnY0WmnggWMNiJALI2uE1xnC6ush1XJ
# ./accounts.py add --username dongbo2 --consumer_key e2unsJ4yjGZVatar6NVU0tfji --consumer_secret Tyf4wrsR15Ow8cHIPRoKIA014VtiZhm5VCP1KlppQuM7pcqsXb --access_token_key 2744107911-yVg1owQk0MZXVEmt1ByIrk1U67x8ZFkFT7yBTmK --access_token_secret AKvNlsDqeyjtmCLuJxsFTCx4ip0AAku4C7zkfQmDw9v3U
