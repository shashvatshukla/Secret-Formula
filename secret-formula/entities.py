import datetime
from google.appengine.ext.ndb import * 

class Asker(Model):
    # key is the google account username, which is the only attribute needed
    pass


class Form(Model):
    # key is auto-generated string (URL-safe, we can use it as URL given to users)
    name    = StringProperty()
    dl      = DateTimeProperty()


class Question(Model):  
    qntext  = StringProperty()
    type    = IntegerProperty() # need to define further after this milestone
    # choices for questions such as check box, radio buttons etc. blank for free response
    options = StringProperty(repeated=True)


class Response(Model):
    subID   = IntegerProperty() # auto_increment, TODO implement
    ans     = StringProperty() # every response type can widen to String