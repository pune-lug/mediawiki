#!/opt/local/bin/python3.2
# -*- coding: utf-8 -*-

'''
This script is currently written for mr.wikipedia.org. It will replace the redirect page with correct page on different wiki pages.
e.g.

[[चेन्नै]] --> Redirected to [[चेन्नई]]
[[चेन्नई]] --> Contents data

This script will search of the pages where [[चेन्नै]] is used and replace it with [[चेन्नई|चेन्नै]].
'''
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
    return parser.parse_args(data)

args = parse_opts(sys.argv[1:])

apdir = args.order
skip = args.skip
user = args.user
password = args.password
site_base_url = args.site
max_edits = args.max_edits

print(skip)
cnt = 0

site = mediawiki.Site(site_base_url)
site.login(user, password)

p = mediawiki.Page(site=site)
cnt = 0
skip_counter = 0

def fix_redirects(skip_counter, list_all=None, max_edits=None):
    global cnt
    if not list_all:
        list_all = site.list_all(apfilterredir='redirects', apdir=apdir)
    while len(list_all) > 0:
        print('Total queried pages: %d' % len(list_all))
        try:
            for list_all_page in list_all:
                skip_counter += 1
                if skip_counter < skip:
                    continue
                if ignore_page(list_all_page):
                    continue
                p.set_title(list_all_page)
                p.get()
                new_link = p.text.split('[[')[1].split(']]')[0]
                if ignore_page(new_link):
                    continue
                print('Skip: %d' % skip_counter)
                back_links = site.list_backlinks(title=list_all_page)
                for back_link_page in back_links:
                    if ignore_page(back_link_page):
                        continue
                    print('Skip counter: %d' % skip_counter)
                    # Uncomment following line if unicode can be displayed properly on your terminal
                    #print('Redirect: %s --- Newlink: %s --- Backlink: %s' % (list_all_page, new_link, back_link_page))
                    p.set_title(back_link_page)
                    p.get()
                    text = p.text.replace('[['+list_all_page+']]', '[['+new_link+'|'+list_all_page+']]').replace('[['+list_all_page+'|', '[['+new_link+'|')
                    if p.text != text:
                        print('editing')
                        p.edit(text)
                        cnt += 1
                        if max_edits and cnt == max_edits:
                            print('%d edits done', cnt)
                            sys.exit()
                    print('Total edits: %d' % cnt)
            list_all = site.list_all(apfilterredir='redirects', apdir=apdir, apcontinue=True)
        except Exception as e:
            print(e)
            print('Total edits: %d' % cnt)
            print('Skip: %d' % skip_counter)
            return(skip_counter)
    return None

try:
    skip_counter = fix_redirects(skip_counter=skip_counter)
except Exception as e:
    print('Skip: %d' % skip_counter)

