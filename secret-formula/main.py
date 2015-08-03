import webapp2
import jinja2
import os
from Crypto.Cipher import AES
from google.appengine.api import users
from google.appengine.ext import db

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
    
    def get(self):
        self.redirect("forms")

class FormMgr(Webpage):
    page = 'FormsMgr.html'
    url = 'forms'
    
    def get(self):
        user = users.get_current_user()
        pk = Key('Asker', user.nickname())
        a = pk.get()
        if a == None:
            a = Asker(id=user.nickname())
            a.put()
        query = gql("select * from Form where ancestor is :1 order by dl desc", pk)
        super(FormMgr, self).get({'userid': user.nickname(), 'forms': query})
    
    def post(self):
        f = Form(parent=Key('Asker', users.get_current_user().nickname()))
        f.name = self.request.get("title")
        f.dl = datetime.datetime.now()
        f.put()
        self.get()

class FormEdit(Webpage):
    page = 'FormEdit.html'
    url = 'editform'
    
		
    def get(self):
        # should not directly access this, use POST from form mgr
        self.redirect(FormMgr.url)
    
    def post(self):
        t = int(self.request.get("type"))
        fid = self.request.get("id")
        k = Key(urlsafe=fid)
        qq = gql("select * from Question where ancestor is :1 order by qno", k)
        
        if t == 1:
            # change to metadata
            f = k.get()
            f.name = self.request.get("title")
            #f.dl = self.request.get("enddate")
            f.put()
            
        if t == 2:
            # change to existing question
            qk = Key(urlsafe=self.request.get("qid"))
            qn = qk.get()
            ntext = self.request.get("qtext")
            ntype = int(self.request.get("qtype"))
            nopt = [i[:-1] if i[-1] == '\r' else i for i in self.request.get("options").split("\n") if i != '' and i != '\r']
            # if nothing changed, we don't waste an unnecessary write
            if qn.text != ntext or qn.type != ntype or qn.options != nopt:
                qn.text = ntext
                qn.type = ntype
                qn.options = nopt
                qn.put()

        if t == 3:
            # new question added
            qn = Question(parent=Key(urlsafe=self.request.get("id")))
            qn.text = self.request.get("qt")
            qn.qno = int(self.request.get("qno"))
            qn.type = 0 # placeholder value, defaults to text box
            qn.put()
            
        if t == 4:
            # delete
            fid = self.request.get("id")        
            db.delete(fid)
            self.redirect(FormMgr.url)
        else:
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
        fk = Key(urlsafe=fid)
        qnos = int(self.request.get("qnos"))
        encrypt_key = self.request.get("key")
        iv = "1234567890123456" #TODO fix this os.urandom(16)
        r = Response(parent=fk)
        r.subID = 1+gql("select subID from Response order by subID desc limit 1").get().subID
        #encryption  code
        # some data redundancy at the moment,
        # should move to an entity that stores metadata about a response to a form
        # as a whole
        #                Wei Liang: FIXED
        r.iv = iv
        encryption_object = AES.new(encrypt_key, AES.MODE_CBC, r.iv)
        r.put()
        
        for i in range(qnos):
            qtype = gql("select type from Question where ancestor is :1 and qno = :2", fk, i).get().type
            if(qtype == 2):
                # check box, need to handle separately
                ans = ""
                for j in self.request.get_all(str(i)):
                    ans += j + ","
                if len(ans) > 0:
                    ans = ans[:-1]
            else:
                ans = self.request.get(str(i))
            
            a = Answer(parent=r.key)
            a.qno = i
            
            a.ans = ans # removed temporarily so I can see the input stored correctly
            # (encryption_object.encrypt(ans)).encode('hex') # encrypt the answer here 
            
            a.put()
        super(Submitted, self).get()
        

class ViewResponse(Webpage):
    page = 'Record.html'
    url = 'viewresponse'
    
    def get(self):
        # should not directly access this, use POST from form mgr
        self.redirect(FormMgr.url)
    
    def post(self):
        fid = self.request.get("id")
        decrypt = self.request.get("key")
        fk = Key(urlsafe=fid)
        f = fk.get()
        # list of questions query
        qq = gql("select * from Question where ancestor is :1 order by qno", fk)
        fk = Key(urlsafe=fid)
        # list of user responses query
        rq = gql("select * from Response where ancestor is :1 order by subID desc", fk)
        tbl = []
        for i in sorted(list(rq.iter()), key=lambda x: x.subID):
            rq = gql("select * from Answer where ancestor is :1 order by qno", i.key)
            tbl += [[j.ans for j in rq.iter()]] # decrypt j.ans here
        super(ViewResponse, self).get({'fid': fid, 'key': decrypt, 'form': f, 'qns': qq, 'tbl': tbl})

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
        #r = Response()
        #r.subID = 0
        #r.ans = "Placeholder response"
        #r.put()
    

pagec = (Main, FormMgr, FormEdit, AnswerForm, Submitted, ViewResponse, Code)
pages = [('/' + i.url, i) for i in pagec]


app = webapp2.WSGIApplication(pages, debug=True)


