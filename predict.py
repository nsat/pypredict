import time
import urllib2
from os import path
from math import ceil
from datetime import datetime
from cpredict import quick_find, quick_predict

def tle(norad_id):
    res = urllib2.urlopen("http://tle.nanosatisfi.com/%s" % str(norad_id))
    if res.getcode() != 200:
        raise urllib2.HTTPError("Unable to retrieve TLE from tle.nanosatisfi.com. HTTP code(%s)" % res.getcode())
    return res.read().rstrip()

class Observer():
    def __init__(self, tle, qth="~/.predict/predict.qth"):
        ## ETL tle and qth data
        self.tle = tle.rstrip().split('\n') if isinstance(tle, basestring) else tle
        if isinstance(qth, basestring):
            raw = open(path.expanduser(qth)).readlines()
            lines = [l.strip() for l in raw]
            assert len(lines) == 4, "qth file '%s' must contain exactly 4 lines (name, lat, long, alt)" % qth
            qth = lines[1:] # remove name
        # Attempt conversion to format required for predict.quick_find
        assert len(qth) == 3, "qth must be (lat, long, alt) as (float, float, int)" 
        self.qth = (float(qth[0]), float(qth[1]), int(qth[2]))

    def observe(self, at = None):
        at = at if at != None else time.time()
        return quick_find(self.tle, at, self.qth)

    # Returns a generator of passes occuring entirely between 'after' and 'before' (epoch)
    def passes(self, after=None, before=None):
        after = after or time.time()
        crs = after
        while True:
            transit = quick_predict(self.tle, crs, self.qth[0:3])
            start = transit[0]['epoch']
            end = transit[-1]['epoch']
            t = Transit(self.tle, self.qth, start, end) # un/repacking for convenient external API
            if (before != None and before < t.end):
                break
            if (t.start > after):
                yield t
            # Need to advance time cursor sufficiently far so predict doesn't yield same pass
            crs = t.end + 60     #seconds seems to be sufficient

# Transit is a convenience class representing a pass of a satellite over a groundstation.
# It is both an internal class (Observer.passes returns an iterator of transits) and an external
# class (importers of the library may instantiate).  
class Transit():
    def __init__(self, tle, qth, start, end):
        self.observer = Observer(tle, qth)
        self.start = start
        self.end = end
        # Let Observer.__init__ handle ETL for us.  Re-use!
        self.qth = self.observer.qth
        self.tle = self.observer.tle

    # return the name of the satellite transiting
    def satellite(self):
        return self.observer.tle[0]

    def max_elevation(self):
        #TODO: Optimize (or at least cache) this.  Also, sub-second granularity?
        return max([self.observer.observe(t)['elevation'] for t in range(int(self.start), int(ceil(self.end)))])

    def duration(self):
        return self.end - self.start

    def at(self, t):
        if self.start <= t <= self.end:
            return self.observer.observe(timestamp)
        else:
            raise LookupError("time %f outside of transit window [%f, %f]" % (t, self.start, self.end))

    def __repr__(self):
        return "Transit%s"%(self.tle, self.qth, self.start, self.end).__repr__()

    def __str__(self):
        return str((self.start, self.end, self.max_elevation(), self.duration()))
