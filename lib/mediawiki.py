import urllib.parse
from http.cookiejar import CookieJar
import json


class Site():
    def __init__(self,
            host=None,
            apiurl='/w/api.php',
            timeout=100,
            srlimit=500,
            apfrom=None,
            aplimit=5000,
            bllimit=5000,
            aulimit=5000,
            aclimit=5000,
            rclimit=5000,
            lelimit=5000,
        ):
        if not host:
            raise(Exception("host not defined"))
        self.host = host
        self.apiurl = apiurl
        self.url = '%s%s' % (self.host, self.apiurl)
        self.format = 'json'
        self.cj = CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cj)
        )
        self.token = None
        self.defaults = {}
        self.defaults['srlimit'] = srlimit
        self.defaults['aplimit'] = aplimit
        self.defaults['aclimit'] = aclimit
        self.defaults['bllimit'] = bllimit
        self.defaults['rclimit'] = rclimit
        self.defaults['lelimit'] = lelimit
        self.srlimit = srlimit
        self.apfrom = apfrom
        self.aplimit = aplimit
        self.bllimit = bllimit
        self.aulimit = aulimit
        self.aclimit = aclimit
        self.rclimit = rclimit
        self.lelimit = lelimit
        self.search_info = {}
        self.aufinished = False

    def return_json(self, data):
        return json.loads(bytes.decode(data, 'utf-8'))

    def sitematrix(self):
        t = {}
        t['action'] = 'sitematrix'
        t['format'] = self.format
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        return self.return_json(f.read())

    def login(self, username=None, password=None):
        self.username = username
        t = {}
        t['action'] = 'login'
        t['lgname'] = username
        t['lgpassword'] = password
        t['format'] = self.format
        self.cj.clear()
        params = urllib.parse.urlencode(t)
        if username:
            f = self.opener.open(self.url, params.encode('utf-8'))
            d = f.read()
            try:
                d = self.return_json(d)
                self.token = d['login']['token']
            except Exception as e:
                raise(Exception('Unable to login:', e))
            if d['login']['result'] == 'NeedToken':
                t['lgtoken'] = d['login']['token']
                params = urllib.parse.urlencode(t)
                f = self.opener.open(self.url, params.encode('utf-8'))
                d = f.read()
                try:
                    d = self.return_json(d)
                    self.token = d['login']['lgtoken']
                except Exception as e:
                    raise(Exception('Unable to login:', e))

    def logout(self):
        t = {}
        t['action'] = 'logout'
        t['format'] = self.format
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
        except Exception as e:
            raise(Exception('Already logged out'))

    def list_backlinks(self, title=None, blcontinue=False, blfilterredir='all', blredirect=False):
        t = {}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'backlinks'
        t['bllimit'] = self.bllimit
        t['blfilterredir'] = blfilterredir
        t['bltitle'] = title
        if blredirect:
            t['blredirect'] = ''
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
        except:
            pass
        retval = []
        try:
            for x in d['query']['backlinks']:
                retval.append(x['title'])
        except:
            pass
        return retval

    def list_allcategories(self, **kargs):
        acfrom = kargs.get('acfrom', None)
        acto = kargs.get('acto', None)
        accontinue = kargs.get('accontinue', None)
        acprefix = kargs.get('acprefix', None)
        t = {}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'allcategories'
        t['aclimit'] = kargs.get('aclimit', self.aclimit)
        t['acdir'] = kargs.get('acdir', 'ascending')
        if acfrom:
            t['acfrom'] = acfrom
        if acto:
            t['acto'] = acto
        if acprefix:
            t['acprefix'] = acprefix
        if not accontinue:
            self.search_info = {}
            self.aclimit = self.defaults['aclimit']
        else:
            if self.aclimit < 0:
                return []
            t['acfrom'] = self.search_info['acfrom']
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            self.search_info = {}
            try:
                self.search_info['acfrom'] = \
                    d['query-continue']['allcategories']['acfrom']
            except:
                pass
            retval = []
            try:
                for x in d['query']['allcategories']:
                    retval.append(x['*'])
            except:
                pass
            if len(retval) < self.srlimit:
                self.srlimit = -1
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def list_all(self, **kargs):
        apcontinue = kargs.get('apcontinue', False)
        t = {}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'allpages'
        t['aplimit'] = self.aplimit
        t['apdir'] = kargs.get('apdir', 'ascending')
        t['apnamespace'] = kargs.get('apnamespace', '0')
        t['apfilterredir'] = kargs.get('apfilterredir', 'all')
        apfrom = kargs.get('apfrom', None)
        apto = kargs.get('apto', None)
        if apfrom:
            t['apfrom'] = apfrom
        if apto:
            t['apto'] = apto
        if not apcontinue:
            self.search_info = {}
            self.aplimit = self.defaults['aplimit']
        else:
            if self.aplimit < 0:
                return []
            t['apfrom'] = self.search_info['apfrom']
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            self.search_info = {}
            try:
                self.search_info['apfrom'] = \
                    d['query-continue']['allpages']['apfrom']
            except:
                pass
            retval = []
            try:
                for x in d['query']['allpages']:
                    retval.append(x['title'])
            except:
                pass
            if len(retval) < self.srlimit:
                self.srlimit = -1
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def search(self, s, srcontinue=False):
        t = {}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'search'
        t['srsearch'] = s
        t['srlimit'] = self.srlimit
        if not srcontinue:
            self.serach_info = {}
            self.srlimit = self.defaults['srlimit']
        if srcontinue and self.srlimit < 0:
            return []
        if srcontinue and s == self.search_info.get('string', ''):
            t['sroffset'] = self.search_info['offset']
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            self.search_info = {}
            self.search_info['string'] = s
            try:
                self.search_info['offset'] = \
                    d['query-continue']['search']['sroffset']
            except:
                pass
            retval = []
            try:
                for x in d['query']['search']:
                    retval.append(x['title'])
            except:
                pass
            if len(retval) < self.srlimit:
                self.srlimit = -1
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def listall(self, srcontinue=False):
        t = {}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'allpages'
        t['aplimit'] = self.aplimit
        if not srcontinue:
            self.apfrom = None
        if srcontinue and self.apfrom:
            t['apfrom'] = self.apfrom
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            self.apfrom = d['query-continue']['allpages']['apfrom']
            retval = []
            for x in d['query']['allpages']:
                retval.append(x['title'])
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def userdailycontribs(self, username=None, daysago=0):
        if not username and self.username:
            username = self.username
        if not username:
            return
        if daysago < 0:
            return
        params = urllib.parse.urlencode({
            'action': 'userdailycontribs',
            'format': self.format,
            'user': username,
            'daysago': daysago,
        })
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            return d
        except Exception as e:
            raise(Exception('Data not found', e))

    def list_allusers(self, **kargs):
        t ={}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'allusers'
        for x in ['aufrom', 'auto', 'audir', 'augroup', 'auexcludegroup', 'aurights', 'auprop', 'aulimit']:
            if kargs.get(x, None):
                t[x] = kargs[x]
        for x in ['auwitheditsonly', 'auactiveusers']:
            if kargs.get(x, None):
                t[x] = ''
        aucontinue = kargs.get('aucontinue', None)
        t['aulimit'] = t.get('aulimit', self.aulimit)
        if not aucontinue:
            self.aufrom = None
            self.aufinished = False
        if aucontinue and self.aufrom:
            t['aufrom'] = self.aufrom
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            try:
                self.aufrom = d['query-continue']['allusers']['aufrom']
            except:
                self.aufinished = True
            retval = []
            for x in d['query']['allusers']:
                retval.append(x['name'])
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def list_recentchanges(self, **kargs):
        t = {}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'recentchanges'
        t['rcprop'] = '|'.join(kargs.get('rcprop', ['title', 'ids', 'type', 'user']))
        t['rclimit'] = self.rclimit
        rctype = kargs.get('rctype', None)
        if rctype:
            t['rctype'] = rctype
        rcstart = kargs.get('rcstart', None)
        rcstop = kargs.get('rcstop', None)
        rccontinue = kargs.get('rccontinue', None)
        if not rccontinue:
            self.rcstart= None
            self.rcfinished = False
        if rccontinue and self.rcstart:
            t['rcstart'] = self.rcstart
        rccontinue = kargs.get('rccontinue', None)
        if rccontinue:
            t['rccontinue'] = rccontinue
        params = urllib.parse.urlencode(t)
        if rcstart:
            params = '%s&rcstart=%s' % (params, rcstart)
        if rcstop:
            params = '%s&rcstop=%s' % (params, rcstop)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            try:
                self.rcstart = d['query-continue']['recentchanges']['rcstart']
            except:
                self.rcfinished = True
            retval = []
            for x in d['query']['recentchanges']:
                tmp_retval = {}
                for y in t['rcprop'].split('|'):
                    if y == 'ids':
                        for z in ['rcid', 'pageid', 'revid', 'old_revid']:
                            tmp_retval[z] = x[z]
                    else:
                        tmp_retval[y] = x[y]
                retval.append(tmp_retval)
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def list_logevents(self, **kargs):
        t = {}
        t['format'] = self.format
        t['action'] = 'query'
        t['list'] = 'logevents'
        letype = kargs.get('letype', None)
        if letype:
            t['letype'] = letype
        t['leprop'] = '|'.join(kargs.get('leprop', ['ids', 'title', 'type', 'user', 'timestamp', 'comment', 'details', 'action']))
        leaction = kargs.get('leaction', None)
        if leaction:
            t['leaction'] = leaction
        lestart = kargs.get('lestart', None)
        if lestart:
            t['lestart'] = lestart
        leend = kargs.get('leend', None)
        if leend:
            t['leend'] = leend
        ledir = kargs.get('ledir', None)
        if ledir:
            t['ledir'] = ledir
        leuser = kargs.get('leuser', None)
        if leuser:
            t['leuser'] = leuser
        letitle = kargs.get('letitle', None)
        if letitle:
            t['letitle'] = letitle
        leprefix = kargs.get('leprefix', None)
        if leprefix:
            t['leprefix'] = leprefix
        letag = kargs.get('letag', None)
        if letag:
            t['letag'] = letag
        t['lelimit'] = kargs.get('lelimit', self.lelimit)
        lecontinue = kargs.get('lecontinue', None)
        if not lecontinue:
            self.lestart= None
            self.lefinished = False
        if lecontinue and self.lestart:
            t['lestart'] = self.lestart
        lecontinue = kargs.get('lecontinue', None)
        if lecontinue:
            t['lecontinue'] = lecontinue
        params = urllib.parse.urlencode(t)
        f = self.opener.open('%s?%s' % (self.url, params))
        d = f.read()
        try:
            d = self.return_json(d)
            try:
                self.lestart = d['query-continue']['logevents']['lestart']
            except:
                self.lefinished = True
            retval = []
            for x in d['query']['logevents']:
                tmp_retval = {}
                for y in t['leprop'].split('|'):
                    if y == 'ids':
                        for z in ['logid', 'pageid']:
                            tmp_retval[z] = x[z]
                    elif y == 'details':
                        pass
                    else:
                        tmp_retval[y] = x[y]
                retval.append(tmp_retval)
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def close(self):
        self.conn.close()


class Page():
    def __init__(self, site):
        self.inprop = [
            'protection',
            'talkid',
            'watched',
            'subjectid',
            'url',
            'readable',
            'preload',
            'displaytitle'
        ]
        self.intoken = [
            'edit',
            'delete',
            'protect',
            'move',
            'block',
            'unblock',
            'email',
            'import',
            'watch'
        ]
        self.site = site

    def exists(self, title):
        t = {}
        t['action'] = 'query'
        t['prop'] = 'revisions'
        t['titles'] = '|'.join(title)
        t['vprop'] = 'timestamp'
        t['format'] = self.site.format
        params = urllib.parse.urlencode(t)
        f = self.site.opener.open('%s?%s' % (self.site.url, params))
        d = f.read()
        try:
            d = self.site.return_json(d)
            tmp = list(d['query']['pages'].keys())
            retval = {}
            retval[True] = []
            retval[False] = []
            for k in tmp:
                if 'revisions' in d['query']['pages'][k]:
                    retval[True].append(d['query']['pages'][k]['title'])
                else:
                    retval[False].append(d['query']['pages'][k]['title'])
                    #retval[d['query']['pages'][k]['title']] = False
            return retval
        except Exception as e:
            raise(Exception('Data not found', e))

    def set_title(self, title):
        self.title = title

    def _set_edittoken(self, data):
        x = data['query']['pages']
        for i in x:
            if x[i].get('edittoken', None):
                self.edittoken = x[i]['edittoken']
                return

    def _set_content(self, data):
        x = data['query']['pages']
        for i in x:
            if x[i].get('revisions', None):
                self.text = x[i]['revisions'][0]['*']
                return

    def get(self, inprop=None, intoken=None):
        if not inprop:
            inprop = self.inprop
        if not intoken:
            intoken = self.intoken
        inprop = '|'.join(self.inprop)
        intoken = '|'.join(self.intoken)
        params = urllib.parse.urlencode({
            'format': self.site.format,
            'action': 'query',
            'prop': 'info|revisions',
            'titles': self.title,
            'inprop': inprop,
            'intoken': intoken,
            'rvlimit': 1,
            'rvprop': 'content',
        })
        f = self.site.opener.open('%s?%s' % (self.site.url, params))
        d = f.read()
        try:
            d = self.site.return_json(d)
            self._set_edittoken(d)
            self._set_content(d)
            return d
        except Exception as e:
            raise(Exception('Data not found', e))

    def edit(self, text=None, minor=True, bot=True, force_edit=False, createonly=False, nocreate=False, md5=None, assert_='user', notminor=False, section=None, summary=None, appendtext=None, prependtext=None):
        if not vars(self).get('text', None):
            self.text = None
        if not force_edit and text == self.text:
            print('Ignoring edit...')
            return
        t = {}
        t['format'] = self.site.format
        t['action'] = 'edit'
        t['title'] = self.title
        t['text'] = text
        t['assert'] = assert_
        if appendtext:
            t['appendtext'] = appendtext
        if prependtext:
            t['prependtext'] = prependtext
        if summary:
            t['summary'] = summary
        if section:
            t['section'] = section
        if minor:
            t['minor'] = ''
        if notminor:
            t['notminor'] = ''
        if bot:
            t['bot'] = ''
        if createonly:
            t['createonly'] = ''
        if nocreate:
            t['nocreate'] = ''
        if md5:
            t['md5'] = md5
        t['token'] = self.edittoken
        params = urllib.parse.urlencode(t)
        self.site.addheaders = [('Content-Type', 'multipart/form-data')]
        f = self.site.opener.open(self.site.url, params.encode('utf-8'))
        d = f.read()
        try:
            d = self.site.return_json(d)
            return d
        except Exception as e:
            raise(Exception('Data not found', e))

    def delete(self, **kargs):
        title = kargs.get('title', None)
        reason = kargs.get('reason', None)
        if not title:
            return
        t = {}
        t['action'] = 'delete'
        t['title'] = title
        t['token'] = self.edittoken
        t['format'] = self.site.format
        if reason:
            t['reason'] = reason
        params = urllib.parse.urlencode(t).encode('utf-8')
        f = self.site.opener.open(self.site.url, params)
        d = f.read()
        try:
            d = self.site.return_json(d)
            return d
        except Exception as e:
            raise(Exception('Data not found', e))

