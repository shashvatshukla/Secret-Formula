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

class Main(Webpage):
    page = 'Main.html'
    url = ''

class FormMgr(Webpage):
    page = 'FormsMgr.html'
    url = 'forms'
    
    def get(self):
        # get the currently logged in user, and find the corresponding Asker entity
        # after which, we load the name of each form that has this Asker as its parent
        
        # if the user doesn't exist in the datastore yet (e.g. first time)
        #     then redirect to a new page to create an 'account' (Asker entity)
        user = users.get_current_user()
        super(FormMgr, self).get({'userid': user.nickname(), 'forms': [1,2,3]})

class FormEdit(Webpage):
    page = 'FormEdit.html'
    url = 'editform'
    
    def get(self):
        # should not directly access this, use POST from form mgr
        self.redirect('../' + FormMgr.url)
    
    def post(self):
        pass


class AnswerForm(Webpage):
    page = 'Answer.html'
    url = 'submitform/' # TODO append form ID and stuff 


class ViewResponse(Webpage):
    page = 'Record.html'
    url = 'viewresponse'
    
    # we can make this work the same way as formedit, make it only accessible via POST 
    


class Code(Webpage):
    page = 'Code.html'
    url = 'code'
    
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
        q = Question()
    

pagec = (Main, FormMgr, FormEdit, AnswerForm, ViewResponse, Code)
pages = [('/' + i.url, i) for i in pagec]


app = webapp2.WSGIApplication(pages, debug=True)
