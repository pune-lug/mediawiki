#!/opt/local/bin/python3.2
# -*- coding: utf-8 -*-

import sys
sys.path.append('mediawiki/lib')
import mediawiki
import re
import argparse
import json

def ignore_page(p):
    if p.startswith('सदस्य:') or p.startswith('साचा:') or p.startswith('वर्ग:') or p.startswith('सदस्य चर्चा:') or p.startswith('सहाय्य:') or p.startswith('विकिपीडिया:'):
        return True
    return False

def update_data(text):
    for x in replace_words:
        text = text.replace(x, replace_words[x])
    for x in replace_regex:
        text = re.sub(x, replace_regex[x], text)
    return text


def generate_regex(a):
    c = a
    a = re.sub('[\u093f\u0940]', '(?:\u093f|\u0940)', a)
    a = re.sub('[\u0941\u0942]', '(?:\u0941|\u0942)', a)
    a = re.sub('[\u0907\u0908]', '(?:\u0907|\u0908)', a)
    a = re.sub('[\u0909\u090a]', '(?:\u0909|\u090a)', a)
    if a != c:
        c = ' '+c+' '
        if c in replace_regex:
            del(replace_regex[c])
        else:
            replace_regex[c] = ' '+a+' '


cnt = 0

def parse_opts(data):
    parser = argparse.ArgumentParser()
    parser.add_argument('--correct-words', default=None)
    parser.add_argument('--replace-words', default=None)
    parser.add_argument('--max-edits', default=None)
    parser.add_argument('--user')
    parser.add_argument('--password')
    parser.add_argument('--site-url', default='http://mr.wikipedia.org')
    return parser.parse_args(data)

args = parse_opts(sys.argv[1:])
site_url = args.site_url
user = args.user
password = args.password
max_edits = args.max_edits
correct_words_file = args.correct_words
replace_words_file = args.replace_words

replace_words = {}
replace_regex = {}
ignore_words_regex = set()



if not correct_words_file and not replace_words_file:
    print('No data available for correction')
    sys.exit(1)


site = mediawiki.Site(site_url)


p = mediawiki.Page(site=site)

cnt = 0
try:
    site.login(user, password)
except Exception as e:
    print('Unable to login')
    sys.exit(1)
p = mediawiki.Page(site=site)

if correct_words_file:
    if correct_words_file.startswith('WPUSERPAGE:'):
        p.set_title("सदस्य:"+user+"/"+correct_words_file.split('WPUSERPAGE:')[1])
        p.get()
        data = p.text
    else:
        data = open(correct_words_file, encoding='utf-8')
    for l in data:
        if l.strip() not in ignore_words_regex:
            generate_regex(l.strip())

if replace_words_file:
    if replace_words_file.startswith('WPUSERPAGE:'):
        p.set_title("सदस्य:"+user+"/"+replace_words_file.split('WPUSERPAGE:')[1])
        p.get()
        data = p.text.split('\n')
    else:
        data = open(replace_words_file, encoding='utf-8')
    for l in data:
        t = json.loads(l)
        for k in t:
            replace_words[k] = t[k]

tot_edits = 0
for n in sorted(replace_words.keys()) + sorted(replace_regex.values()):
    try:
        print(n)
    except:
        pass
    pages = site.search(n)
    while len(pages):
        if pages:
            for page in pages:
                if ignore_page(page):
                    continue
                print(page)
                tot = 0
                p.set_title(page)
                p.get()
                text_orig = '%s' % p.text
                text = update_data(p.text)
                if text_orig != text:
                    print('editing')
                    p.edit(text)
                    tot_edits += 1
                    if max_edits and tot_edits == max_edits:
                        print('Total edits: %d' % tot_edits)
                        sys.exit()
                else:
                    print('no change')
        try:
            pages = site.search(n, srcontinue=True)
        except Exception as e:
            print(e)
            sys.exit()



print('Total edits', tot_edits)
try:
    site.logout()
except Exception as e:
    print(e)
