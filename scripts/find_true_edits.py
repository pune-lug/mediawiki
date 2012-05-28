#!/opt/local/bin/python2.7
# -*- coding: utf-8 -*-

import mwclient
site = mwclient.Site('mr.wikipedia.org')
user = raw_input('Enter user:')
uc = site.usercontributions(user)
c = []
i = 0
def is_valid(x):
    if x.find('HotCat') == -1 and x.find(u'नवीन पान') == -1 and x.find(u'या संचिकेची नवीन आवृत्ती चढविली') == -1 and x.find('AWB') == -1 and x.find(u'कडे पुनर्निर्देशित') == -1 and x.find(u'मथळ्याखाली स्थानांतरित केले.') == -1 and x.find(u'मथळ्या') == -1 and x.find(u'यांची आवृत्ती') == -1 and x.find(u'स्वागत') == -1 and x.find('Robot') == -1:
        return True
    else:
        return False

for x in uc:
    #c.add(x[u'comment'])
    if is_valid(x[u'comment']):
        c.append(x[u'comment'])
    i += 1
    if not i%1000: print i

#d = [ x for x in c if x.find('HotCat') == -1 and x.find(u'नवीन पान') == -1 and x.find(u'या संचिकेची नवीन आवृत्ती चढविली') == -1 and x.find('AWB') == -1 and x.find(u'कडे पुनर्निर्देशित') == -1 and x.find(u'मथळ्याखाली स्थानांतरित केले.') == -1 and x.find(u'मथळ्या') == -1 and x.find(u'यांची आवृत्ती') == -1 and x.find(u'स्वागत') == -1 and x.find('Robot') == -1]
#print len(d), i, (len(d)*100.0/i)
no_comments = len([x for x in c if not x])
print len(c), i, (len(c)*100.0/i), (len(set(c))+no_comments)*100.0/i

