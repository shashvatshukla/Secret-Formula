import webapp2
import jinja2
import os
from google.appengine.api import users

jjenv = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/res/webpage"))

import datetime
from entities import *

class Webpage(webapp2.RequestHandler):
    def get(self, args = {}):
        tmp = jjenv.get_template(self.page)
        self.response.write(tmp.render(args))

class AuthWebpage(Webpage):
    def get(self):
        user = users.get_current_user()
        super(AuthWebpage, self).get({'userid': user.nickname()})

class Main(Webpage):
    page = 'Main.html'
    url = '/'

class FormMgr(AuthWebpage):
    page = 'FormsMgr.html'
    url = '/forms'

class Code(Webpage):
    page = 'Code.html'
    url = '/code'
    
    def get(self):
        super(Code, self).get()
        # write arbitrary code here. treat this as your admin terminal
        # remember to delete or comment out everything after use, to avoid accidental runs
        
        #a = Asker(id="TestGuy")
        #a.put()
        #f = Form(parent=Key('Asker', 'TestGuy'))
        #f.name = "Test Form 1"
        #f.dl = datetime.datetime.now()
        #f.put()
        #g = Form(parent=Key('Asker', 'TestGuy'))
        #g.name = "Test Form 2"
        #g.dl = datetime.datetime.now()
        #g.put()
        
    

pagec = (Main, FormMgr, Code)
pages = [(i.url, i) for i in pagec]


app = webapp2.WSGIApplication(pages, debug=True)
