from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.dist import use_library
use_library('django', '1.2')


from google.appengine.ext.db import GeoPt
from google.appengine.ext import db

import os
from google.appengine.ext.webapp import template

from models import Sighting
from models import AttachedImage

from geopy import geocoders

from geohash import Geohash


from django.utils import simplejson  
import models

import EXIF
import exif_helper 
import cStringIO

import logging

class GetSightingsAsJson(webapp.RequestHandler):
    def get(self):
        q = Sighting.all()
        points = []
        for result in q:
            point = {}
            if result.coords:
                point['lat'] = result.coords.lat
                point['lon'] = result.coords.lon
                point['address'] = result.address
                image = AttachedImage.gql("WHERE sighting = :1", result).get()
                if image:
                    point['thumbnail'] = "/show_image?id=%s&size=thumb" % image.key().id()
                points.append(point)
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(simplejson.dumps(points) );

class ShowImage(webapp.RequestHandler):
    def get(self):
        id    = None
        size  = "thumb"

        try:
            id = int(self.request.get('id'))
            logging.info("Got id %s", id);
        except ValueError:
            pass

        size = self.request.get('size')

        if id:
            image = AttachedImage.get_by_id(id)
            logging.info("Got image %s", id);
            self.response.headers['Content-Type'] = "image/jpg"
            if size == "thumb":
                self.response.out.write(image.get_thumbnail())
            elif size == "original":
                self.response.out.write(image.original)
            else:
                self.response.out.write(image.get_small())
        
class ViewSighting(webapp.RequestHandler):
    def get(self):
        id = None
        try:
            id = int(self.request.get('id'))
            logging.info("Got id %s", id);
        except ValueError:
            pass
        if id:
            sighting = Sighting.get_by_id(id)
            logging.info("Got sighting %s", sighting.coords)
            images = AttachedImage.gql("WHERE sighting = :1", sighting).fetch(10,0)

            for image in images:
                logging.info("Got image id = %s", image.key())

            template_params = {
                    'images': images,
                    'sighting': sighting
                    }   
        path = os.path.join(os.path.dirname(__file__), 'templates/TestTemplat.html')
        self.response.out.write(template.render(path, template_params))

class RecordSighting(webapp.RequestHandler):
    def get(self):
        address = ""
        lat = ""
        long = ""
        id= None
        species = ""
        geohash = ""
        try:
            id = int(self.request.get('id'))
            logging.info("Got id %s", id);
        except ValueError:
            pass

        template_params = {
                'sighting': None
                }   
        if id:
            template_params['sighting'] = Sighting.get_by_id(id)

        q = Sighting.all()
        all_sightings = []
        for result in q:
            all_sightings.append(result)

        template_params['all_sightings'] = all_sightings

        path = os.path.join(os.path.dirname(__file__), 'templates/record_sighting_form.html')
        self.response.out.write(template.render(path, template_params))

    def post(self):
        logging.info("Entering POST")
        userprefs = models.get_userprefs()
        sighting = models.Sighting()
        logging.info("Entering POST")

        image = None
        lat = None
        lon = None

        for param in ['address','lat','long']:
            if self.request.get(param):
                logging.info('Got params %s = %s', param, self.request.get(param))
                #logging.info('Got params %s = %s' % param, self.request.get(param))

        if self.request.get('address'):
            sighting.address = self.request.get('address')
            logging.info("Got addres = '%s'",sighting.address)
            g = geocoders.Google()
            try:
                place, (lat, lon) = g.geocode(sighting.address)  
                logging.info("Geocode result: %s: %.5f, %.5f" % (place, lat, lon)  )
            except ValueError as (geocode_error):
                logging.info("Geocoding error: %s", geocode_error);

        if self.request.get('img'):
            image = models.AttachedImage()
            image.original = self.request.get('img')
            imageStream = cStringIO.StringIO(image.original)
            data = EXIF.process_file(imageStream, stop_tag='UNDEF', details=True, strict=False, debug=False)
            try:
                lat, lon = exif_helper.get_gps_coords(data)
                logging.info("got img coords %s %s",   lat, lon)
            except:
                logging.info("Image eotagging failed")

        if lat and lon:
            sighting.geohash = str(Geohash((lat, lon)));
            sighting.coords = GeoPt(lat, lon);
            logging.info("geohash is %s", sighting.geohash);
        else:
            self.redirect('/record_sighting?=NO LOCATION ERROR')


        if not sighting.address:
            sighting.address = "%s, %s" %(lat, lon)
            logging.info("Writing address as %s", sighting.address)

        sighting.comment = self.request.get('comment')
        sighting.spieces = self.request.get('species')
        logging.info("Sighting is %s", sighting);
        sighting.put();

        if image:
            image.sighting = sighting.key()
            image.put()
            logging.info("image Key is %s", image.key().id());

        logging.info("Key is %s", sighting.key().name());
        logging.info("Key is %s", sighting.key().id());

        #except :
        #    logging.info("Generic error");
        #    self.redirect('/record_sighting?=ERRORgeneral')

        self. redirect('/record_sighting?id=%s' % (sighting.key().id()))

application = webapp.WSGIApplication([('/record_sighting', RecordSighting),
                                      ('/show_image', ShowImage),
                                      ('/get_sightings', GetSightingsAsJson),
                                      ('/view_sighting',ViewSighting)  
],
                                     debug=True)
def main():
    run_wsgi_app(application)
if __name__ == ' __main__':
    main()

