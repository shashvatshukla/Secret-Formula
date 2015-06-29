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
        pk = Key('Asker', "TestGuy")
        query = gql("select * from Form where ancestor is :1 order by dl desc", pk)
        super(FormMgr, self).get({'userid': user.nickname(), 'forms': query})

class FormEdit(Webpage):
    page = 'FormEdit.html'
    url = 'editform'
    
    def get(self):
        # should not directly access this, use POST from form mgr
        self.redirect('../' + FormMgr.url)
    
    def post(self):
        t = int(self.request.get("type"))
        fid = self.request.get("id")
        k = Key(urlsafe=fid)
        qq = gql("select * from Question where ancestor is :1 order by qno", k)
        
        if t == 1:
            # change to metadata
            f = k.get()
            f.name = self.request.get("title")
            f.dl = self.request.get("enddate")
            f.put()
            
        if t == 2:
            # change to existing question
            qk = Key(urlsafe=self.request.get("qid"))
            qn = qk.get()
            nt = self.request.get("qtext")
            if qn.qtext != nt: # if nothing changed, we don't waste an unnecessary write
                qn.qtext = nt
                qn.put()

        if t == 3:
            # new question added
            qn = Question(parent=Key(urlsafe=self.request.get("id")))
            qn.qtext = self.request.get("qt")
            qn.qno = int(self.request.get("qno"))
            qn.put()
            
        super(FormEdit, self).get({'type': t, 'form': k.get(), 'questions': qq})


class AnswerForm(Webpage):
    page = 'Answer.html'
    url = 'answerform'
    
    def get(self):
        fid = self.request.get("id")
        k = Key(urlsafe=fid)
        qq = gql("select * from Question where ancestor is :1 order by qno", k)
        super(AnswerForm, self).get({'form': k.get(), 'questions': qq})

class Submitted(Webpage):
    page = 'Submit.html'
    url = 'submitted'
    
    def get(self):
        pass
        # not supposed to be accessed via GET, but also no meaningful redirect, so meh
    
    def post(self):
        fid = self.request.get("id")
        qno = self.request.get("qno")
        ans = [self.request.get(str(i+1)) for i in range(qno)]
        # insert answers into datastore

class ViewResponse(Webpage):
    page = 'Record.html'
    url = 'viewresponse'
    
    def get(self):
        # should not directly access this, use POST from form mgr
        self.redirect('../' + FormMgr.url)
    
    def post(self):
        pass


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
        #q = Question()
    

pagec = (Main, FormMgr, FormEdit, AnswerForm, Submitted, ViewResponse, Code)
pages = [('/' + i.url, i) for i in pagec]


app = webapp2.WSGIApplication(pages, debug=True)
