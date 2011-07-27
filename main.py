#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users

import datetime
import models


class MainHandler(webapp.RequestHandler):
    def get(self):
        time = datetime.datetime.now()
        user = users.get_current_user()

        if not user:
            navbar = ('<p>Welcome! <a href="%s">Sign in or register</a> to customize.</p>'
                  % (users.create_login_url(self.request.path)))
            tz_form = ''
        else:
            userprefs = models.get_userprefs();
            navbar = ('<p>Welcome, %s! You can <a href="%s">sign out</a>.</p>'
                  % (user.email(), users.create_logout_url(self.request.path)))
            tz_form = '''<form action="/prefs" method="post">
                             <label for="tz_offset">
                                 Timezone offset from UTC (can be negative):
                             </label>
                             <input name="tz_offset" id="tz_offset" type="text"
                                 size="4" value="%d" />
                             <input type="submit" value="Set" />
                         </form>
                     ''' % userprefs.tz_offset
            time += datetime.timedelta(0, 0, 0, 0, 0, userprefs.tz_offset)
            self.response.out.write(userprefs.key().name())
            self.response.out.write(userprefs.key())

        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('''
        <html>
            <head>
            <title>The Time Is...</title>
            </head>
         <body>
            %s
            <p>The time is: %s</p>
            %s
            </body>
        </html>
        ''' % (navbar, str(time), tz_form))

class MainHandler2(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('test world!\n')
        self.response.out.write('test world!')
        self.response.out.write('test world!')
def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                          ('/test', MainHandler2)
],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
