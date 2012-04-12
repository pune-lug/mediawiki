#!/opt/local/bin/python3.2
# -*- coding: utf-8 -*-

import sys
import time
import getpass
import argparse

from pprint import pprint

# Change this according to the location of mediawiki module
sys.path.append('mediawiki/lib')
import mediawiki
welcome_msg = '{{स्वागत}}'
page_prefix = 'सदस्य_चर्चा:'

def parse_opts(data):
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip', default=0, type=int)
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--site', default='http://mr.wikipedia.org')
    parser.add_argument('--max-edits', type=int, default=0)
    parser.add_argument('--users-file', default=None)
    return parser.parse_args(data)

args = parse_opts(sys.argv[1:])

skip = args.skip
user = args.user
password = args.password
site_base_url = args.site
max_edits = args.max_edits

skip_users = set()

if args.users_file:
    try:
        for l in open(args.users_file):
            skip_users.add(l.strip())
    except:
        pass

print(skip)
cnt = 0

site = mediawiki.Site(site_base_url)
site.login(user, password)

cnt = 0
skip_counter = 0

users = None

p = mediawiki.Page(site=site)

if args.users_file:
    f = open(args.users_file, 'w')
else:
    f = None
users_update = []
edit_cnt = 0
if not users:
    users = site.list_logevents(letype='newusers')
try:
    while len(users) > 0:
        print('Queried: %d --- %d' % (len(users), site.lelimit))
        titles = []
        for user in users:
            if user['action'] != 'create':
                continue
            cnt += 1
            if user['title'] in skip_users:
                if f:
                    f.write('%s\n' % user)
                continue
            if skip > cnt:
                continue
            users_update.append(user['title'])
        while users_update:
            tmp_users_update = users_update[:50]
            users_update = users_update[50:]
            tmp_titles = []
            for x in tmp_users_update:
                tmp_titles.append(x.replace('सदस्य:', 'सदस्य_चर्चा:'))
            r = p.exists(tmp_titles)
            print(r)
            for title in r[False]:
                p.set_title(title)
                p.get()
                print(p.edit(welcome_msg, createonly=True))
                edit_cnt += 1
                if f:
                    f.write('%s\n' % user)
                if max_edits and max_edits < edit_cnt:
                    print('%d --- %d' % (max_edits, edit_cnt))
                    sys.exit()
        if len(users) == site.lelimit:
            users = site.list_logevents(letype='newusers', lecontinue=True)
        else:
            users = []
except Exception as e:
    print(e)
    print('Skip counter: %d' % cnt)
    print('Total Edits: %d' % edit_cnt)

