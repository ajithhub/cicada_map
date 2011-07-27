from google. appengine.ext import webapp
from google. appengine.ext.webapp.util import run_wsgi_app

from google.appengine.ext.db import GeoPt
from google.appengine.ext import db
from models import Sighting

from geopy import geocoders

import models

import logging

class RecordSighting(webapp.RequestHandler):
    def get(self):
        address = ""
        lat = ""
        long = ""
        id= None
        try:
            id = int(self.request.get('id'))
            logging.info("Got id %s", id);
        except ValueError:
            pass

        if id:
            #key = db.Key.from_path('Sighting', id)
            #logging.info("Got key %s", key);
            #logging.info("Got key id %s", key.id());
            sighting = Sighting.get_by_id(id)
            logging.info("Got sighting %s", sighting.coords);
            
            address = sighting.address
            lat = sighting.coords.lat
            long = sighting.coords.lon

        self.response.out.write('''
        <html>
            <head>
            <title>Record a new sighting...</title>
            </head>
         <body>
            <form action = "record_sighting" method = "POST">
Address: <input name = "address" type = "text" value = "%s"/><br>
Lat: <input disabled name = "lat"  type = "text" value = "%s"/><br>
long: <input disabled name = "long" type = "text" value = "%s" /><br>
submit: <input name  = "save" type = "submit"/><br>

</form>
         </body>
        </html>
        '''%( address, lat, long))

        self.response.out.write("<table>");
        q = Sighting.all()
        for result in q:
            self.response.out.write("<tr><td>%s(%s, %s)</td></tr>" % (result.address, result.coords.lat, result.coords.lon))
        self.response.out.write("</table>");

    def post(self):
        userprefs = models.get_userprefs()
        sighting = models.Sighting()
        try:
            for param in ['address','lat','long']:
                if self.request.get(param):
                    logging.info('Got params %s = %s', param, self.request.get(param))
                    #logging.info('Got params %s = %s' % param, self.request.get(param))
            sighting.address = self.request.get('address')
            g = geocoders.Google()
            place, (lat, lng) = g.geocode(sighting.address)  
            logging.info("%s: %.5f, %.5f" % (place, lat, lng)  )
            sighting.coords = GeoPt(lat, lng);
            #sighting.coords = GeoPt(self.request.get('lat'),self.request.get('long'));
            logging.info("Sighting is %s", sighting);
            sighting.put();
            logging.info("Key is %s", sighting.key().name());
            logging.info("Key is %s", sighting.key().id());
        except ValueError:
            # User entered a value that wasn't an integer.  Ignore for now.
            self. redirect('/record_sighting?=ERROR')

        self. redirect('/record_sighting?id=%s' % (sighting.key().id()))

application = webapp.WSGIApplication([('/record_sighting', RecordSighting)],
                                     debug=True)
def main():
    run_wsgi_app(application)
if __name__ == ' __main__':
    main()

