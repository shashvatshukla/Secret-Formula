import webapp2
import jinja2
import os
from Crypto.Cipher import AES
from google.appengine.api import users
from google.appengine.ext import db
import random

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
        super(Main, self).get();

class Invalid(Webpage):
    page = 'Invalid.html'
    url = 'invalid'
    
    def get(self):
        super(Invalid, self).get();

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
        
        if k.parent().id() !=  users.get_current_user().nickname():
            self.redirect(Invalid.url)
        else:
            qq = gql("select * from Question where ancestor is :1 order by qno", k)
            
            if t == 1:
                # change to metadata
                f = k.get()
                f.name = self.request.get("title")
                f.dl = datetime.datetime.strptime(self.request.get("dl"), "%Y-%m-%dT%H:%M")
                f.put()
                
            if t == 2:
                # change to existing question
                qk = Key(urlsafe=self.request.get("qid"))
                qn = qk.get()
                ntext = self.request.get("qtext")
                ntype = int(self.request.get("qtype"))
                nmust = self.request.get("comp") != ''
                nopt = [i[:-1] if i[-1] == '\r' else i for i in self.request.get("options").split("\n") if i != '' and i != '\r']
                # if nothing changed, we don't waste an unnecessary write
                if qn.text != ntext or qn.type != ntype or qn.must != nmust or qn.options != nopt:
                    qn.text = ntext
                    qn.type = ntype
                    qn.must = nmust
                    qn.options = nopt
                    qn.put()
    
            if t == 3:
                # new question added
                qn = Question(parent=Key(urlsafe=self.request.get("id")))
                qn.text = self.request.get("qt")
                qn.qno = int(self.request.get("qno"))
                qn.must = False # defaults to non-compulsory
                qn.type = 0     # defaults to simple text
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
        f = k.get()
        qq = None
        late = f.dl < datetime.datetime.now()
        if not late:
            qq = gql("select * from Question where ancestor is :1 order by qno", k)
        super(AnswerForm, self).get({'form': f, 'questions': qq, 'late': late})

class Submitted(Webpage):
    page = 'Submit.html'
    url = 'submit'
    
    def get(self):
        pass
        # not supposed to be accessed via GET, but also no meaningful redirect, so meh
    
    def post(self):
        fid = self.request.get("id")
        fk = Key(urlsafe=fid)
        qnos = int(self.request.get("qnos"))
        encrypt_key = self.request.get("key")
        probkey = None
        problemq = []
        if len(encrypt_key)%16:
            probkey = encrypt_key
        else:
            charset = "\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e"
            iv = ""
            for i in range(16):
                iv+=random.choice(charset)
            #iv = "1234567890123456" #for debugging 
            r = Response(parent=fk)
            r.subID = 1+gql("select subID from Response order by subID desc limit 1").get().subID
            r.iv = iv
            encryption_object = AES.new(encrypt_key, AES.MODE_CBC, r.iv)
            r.put()
            
            to_add = []    # queue of entities to write to datastore
            
            for i in range(qnos):
                q = gql("select type, must from Question where ancestor is :1 and qno = :2", fk, i).get()
                qtype = q.type
                qmust = q.must
                if(qtype == 2):
                    # check box, need to handle separately
                    ans = ""
                    for j in self.request.get_all(str(i)):
                        ans += j + ","
                    if len(ans) > 0:
                        ans = ans[:-1]
                else:
                    ans = self.request.get(str(i))
                    if qmust and ans == '':
                        problemq.append(i+1)
                
                ans += " " * (16-len(ans)%16) # make string a multiple of 16 letters for encryption
                a = Answer(parent=r.key)
                a.qno = i
                a.ans = (encryption_object.encrypt(ans)).encode('hex') # encrypt_key the answer here
                
                to_add.append(a)
            
            # put the datastore writes together, if something goes wrong beforehand we can skip this
            if problemq:
                r.key.delete()
            else:
                for i in to_add:
                    i.put()
        
        super(Submitted, self).get({'key': probkey, 'pq': problemq})
        

class ViewResponse(Webpage):
    page = 'Record.html'
    url = 'viewresponse'
    
    def get(self):
        # should not directly access this, use POST from form mgr
        self.redirect(FormMgr.url)
    
    def post(self):
        fid = self.request.get("id")
        decrypt_key = self.request.get("key")
        fk = Key(urlsafe=fid)
        if fk.parent().id() !=  users.get_current_user().nickname():
            self.redirect(Invalid.url)
        else:
            f = fk.get()
            # list of questions query
            qq = gql("select * from Question where ancestor is :1 order by qno", fk)
            fk = Key(urlsafe=fid)
            # list of user responses query
            rq = gql("select * from Response where ancestor is :1 order by subID desc", fk)
            tbl = []
            
            errcount = 0
            
            if decrypt_key:
                if len(decrypt_key)%16:
                    errcount = -1
                else:
                    for i in sorted(list(rq.iter()), key=lambda x: x.subID):
                        
                        decryption_object = AES.new(decrypt_key,AES.MODE_CBC, i.iv)
                        aq = gql("select * from Answer where ancestor is :1 order by qno", i.key)
                        
                        #tbl += [[j.ans for j in aq.iter()]] # when decryption doesnt work, debugging
                        
                        row = []
                        err = 0
                        
                        for j in aq.iter():
                            try:
                                row += [decryption_object.decrypt(j.ans.decode('hex'))]
                                row[-1].encode('utf8')
                            except UnicodeDecodeError:
                                err = 1
                                break
                        
                        if err == 0:
                            tbl += [row]
                        else:
                            errcount += 1
            
            super(ViewResponse, self).get({'fid': fid, 'key': decrypt_key, 'form': f, 'qns': qq, 'tbl': tbl, 'err': errcount})

class Code(Webpage):
    page = 'Code.html'
    url = 'code'
    
    def get(self):
        super(Code, self).get()
        # write arbitrary code here. treat this as your admin terminal
        # remember to delete or comment out everything after use, to avoid accidental runs
        
    

pagec = (Main, Invalid, FormMgr, FormEdit, AnswerForm, Submitted, ViewResponse, Code)
pages = [('/' + i.url, i) for i in pagec]


app = webapp2.WSGIApplication(pages, debug=True)


