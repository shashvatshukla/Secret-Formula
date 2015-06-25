import webapp2

class Webpage(webapp2.RequestHandler):
    def get(self):
        with open('res/webpage/'+self.page, 'r') as f: 
            for l in f:
                self.response.write(l)


class Main(Webpage):
    page = 'Main.html'
    url = '/'


class Login(Webpage):
    page = 'Login.html'
    url = '/login'


pagec = (Main, Login)
pages = [(i.url, i) for i in pagec]


app = webapp2.WSGIApplication(pages, debug=True)
