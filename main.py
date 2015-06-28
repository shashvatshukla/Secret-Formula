import webapp2
import jinja2
import os
from google.appengine.api import users

jjenv = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/res/webpage"))

class Webpage(webapp2.RequestHandler):
    def get(self, args = {}):
        tmp = jjenv.get_template(self.page)
        self.response.write(tmp.render(args))

class AuthWebpage(Webpage):
    def get(self):
        user = users.get_current_user()
        if user:
            super(AuthWebpage, self).get({'userid': user})
        else:
            self.redirect('../login')

class Main(Webpage):
    page = 'Main.html'
    url = '/'

class FormMgr(AuthWebpage):
    page = 'FormsMgr.html'
    url = '/forms'


pagec = (Main, FormMgr)
pages = [(i.url, i) for i in pagec]


app = webapp2.WSGIApplication(pages, debug=True)
