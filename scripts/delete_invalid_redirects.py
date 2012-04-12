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


def ignore_page(p):
    '''
    Do not change special pages
    '''
    if p.startswith('सदस्य:') or p.startswith('साचा:') or p.startswith('वर्ग:') or p.startswith('सदस्य चर्चा:') or p.startswith('सहाय्य:') or p.startswith('विकिपीडिया:'):
        return True
    return False

def parse_opts(data):
    parser = argparse.ArgumentParser()
    parser.add_argument('--order', default='ascending')
    parser.add_argument('--skip', default=0, type=int)
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--site', default='http://mr.wikipedia.org')
    parser.add_argument('--max-edits', default=None)
    parser.add_argument('--apfrom', default=None)
    return parser.parse_args(data)

args = parse_opts(sys.argv[1:])

apdir = args.order
skip = args.skip
user = args.user
password = args.password
site_base_url = args.site
apfrom = args.apfrom
max_edits = args.max_edits

print(skip)
cnt = 0

site = mediawiki.Site(site_base_url)
site.login(user, password)

p = mediawiki.Page(site=site)
cnt = 0
skip_counter = 0
# Get edit/delete token
p.set_title('Main_Page')
p.get()


cnt = 0
pages = site.list_all(apfilterredir='redirects', apdir=apdir, apfrom=apfrom)
while len(pages) > 0:
    print('Len: %d' % len(pages))
    for page in pages:
        print(page)
        skip_counter += 1
        if skip > skip_counter:
            continue
        p.set_title(page)
        p.get()
        link = p.text.split('[[')[1].split(']]')[0]
        if p.exists([link])[False]:
            print(p.delete(title=page, reason='Redirect page does not exist'))
            cnt += 1
        if max_edits and cnt == max_edits:
            sys.exit()
    pages = site.list_all(apfilterredir='redirects', apdir=apdir, apcontinue=True)
