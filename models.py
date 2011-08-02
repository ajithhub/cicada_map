from google.appengine.api import users
from google.appengine.ext import db

import logging
from google.appengine.api import memcache
#PIL
from google.appengine.api import images

class Sighting(db.Model):
    coords  = db.GeoPtProperty()
    geohash = db.StringProperty()
    species = db.StringProperty()
    address = db.PostalAddressProperty()
    email   = db.EmailProperty()
    comment = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
 
class AttachedImage(db.Model):
    caption = str
    original  = db.BlobProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    sighting = db.ReferenceProperty(Sighting)

    def resize(self, w, h):
        if not self.original:
            return None
        img = images.Image(self.original)
        img.resize(width=w, height=h)
        img.im_feeling_lucky()
        return img.execute_transforms(output_encoding=images.JPEG)
    def get_thumbnail(self):
        return self.resize(80,100)
    def get_small(self):
        return self.resize(640,480)


class UserPrefs(db.Model):
    tz_offset = db.IntegerProperty(default=0)
    user      = db.UserProperty(auto_current_user_add=True)
    

    def cache_set(self):
        logging.info("Cache set with key = %s" % self.key().name())
        memcache.set(self.key().name(), self,
            namespace=self.key().kind())

    def put(self):
        self.cache_set()
        db.Model.put(self)
        


def get_userprefs(user_id=None):
    if not user_id:
        user = users.get_current_user()
        if not user:
            return None
        user_id = user.user_id()

    userprefs = memcache.get(user_id, namespace='UserPrefs')

    if not userprefs:
        logging.info("Cache miss for user %s" % user_id);
        key = db.Key.from_path('UserPrefs', user_id)
        userprefs = db.get(key)
    else:
        logging.info("Cache hit for user");

    if userprefs:
        userprefs.cache_set()
    else:
        userprefs = UserPrefs(key_name=user_id)

    return userprefs

