import sys
import urllib2
import json

from django.utils.http import urlquote

class LatLng:
    """
    Send an address to Geocoder API (Google) and get JSON output back.
    Parse to retrieve latitude and longitude.
    There is a 24-hour usage limit, currently this is 2500 requests 
    but this could change in the future. Check Google's Terms of Use
    before employing this technique.
    USAGE:
    >>> location = "1600 Amphitheatre Parkway, Mountain View, CA 94043"
    >>> glatlng = LatLng()
    >>> glatlng.requestLatLngJSON(location)
    >>> print "Latitude: %s, Longitude: %s" % (glatlng.lat, glatlng.lng)
    Latitude: 37.422782, Longitude: -122.085099`
    """
    def __init__(self):
        self.lat = ""
        self.lng = ""
        self.results = ""

    def parseResults(self, buff):
        self.results = json.loads(buff)
        try:
                self.lat = self.results['results'][0]['geometry']['location']['lat']
                self.lng = self.results['results'][0]['geometry']['location']['lng']
        except:
                print >> sys.stderr, "An error occurred.\nQuery results: %s" % self.results

    def requestLatLngJSON(self, location):
        self.location = location
        self.url = u'http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=%s' % urlquote(location)
        r = urllib2.urlopen(self.url)
        buff = r.read()
        self.parseResults(buff)