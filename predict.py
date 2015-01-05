import os
import time
import urllib2
from os import path
from cpredict import quick_find, quick_predict, PredictException

def tle(sat_id):
    try:
        res = urllib2.urlopen("http://tle.nanosatisfi.com/%s" % str(sat_id))
        if res.getcode() != 200:
            raise urllib2.HTTPError("Unable to retrieve TLE from tle.nanosatisfi.com. HTTP code(%s)" % res.getcode())
        return res.read().rstrip()
    except Exception as e:
        raise PredictException(e)

def massage_tle(tle):
    try:
        # TLE may or may not have been split into lines already
        if isinstance(tle, basestring):
            tle = tle.rstrip().split('\n')
        assert len(tle) == 3, "TLE must be 3 lines, not %d: %s" % (len(tle), tle)
        return tle
        #TODO: print a warning if TLE is 'too' old
    except Exception as e:
        raise PredictException(e)

def massage_qth(qth):
    try:
        # QTH may or may not have been converted into 3-tuple
        if isinstance(qth, basestring):
            qth = qth.rstrip().split('\n')
            assert len(qth) == 4, "'%s' must contain exactly 4 lines: name, lat(N), long(W), alt(m)" % qth
            qth = qth[1:] # remove name
        assert len(qth) == 3, "%s must consist of exactly three elements: (lat(N), long(W), alt(m))" % qth
        # Attempt conversion to format required for predict.quick_find
        return (float(qth[0]), float(qth[1]), int(qth[2]))
    except ValueError as e:
        raise PredictException("Unable to convert '%s' (%s)" % (qth, str(e)))
    except Exception as e:
        raise PredictException(e)

def host_qth():
    try:
        qth_path = os.path.abspath(os.path.expanduser("~/.predict/predict.qth"))
        with open(qth_path) as qthfile:
            return massage_qth(qthfile.read())
    except IOError as e:
        raise PredictException("Unable to open '%s' (%s)" % (qth_path, str(e)))

class Observer():
    def __init__(self, tle, qth=None):
        self.qth = host_qth() if (qth is None) else massage_qth(qth)
        self.tle = massage_tle(tle)

    def observe(self, at=None):
        at = time.time() if (at is None) else at
        return quick_find(self.tle, at, self.qth)

    # Returns a generator of transits that overlap the 'start' to 'stop' time interval
    def passes(self, start=None, stop=None):
        start = time.time() if (start is None) else start
        ts = start
        while True:
            transit = quick_predict(self.tle, ts, self.qth)
            t = Transit(self.tle, self.qth, start=transit[0]['epoch'], end=transit[-1]['epoch'])
            if (stop != None and t.start >= stop):
                break
            if (t.end > start):
                yield t
            # Need to advance time cursor so predict doesn't yield same pass
            ts = t.end + 60     #seconds seems to be sufficient

# Transit is a convenience class representing a pass of a satellite over a groundstation.
class Transit():
    def __init__(self, tle, qth, start, end):
        self.end = end
        self.start = start
        # tle & qth may not be valid here (since library importer can instantiate a Transit)
        # We re-use the Observer class to perform input conversion
        self.engine = Observer(tle, qth)
        self.qth = self.engine.qth
        self.tle = self.engine.tle

    # return observation within epsilon seconds of maximum elevation
    def peak(self, epsilon=0.1):
        ts =  (self.end + self.start)/2
        step = (self.end - self.start)
        while (step > epsilon):
            step /= 4
            # Ascend the gradient at this step size
            direction = None
            while True:
                mid   = self.engine.observe(ts)['elevation']
                left  = self.engine.observe(ts - step)['elevation']
                right = self.engine.observe(ts + step)['elevation']
                # Break if we're at a peak
                if (left <= mid >= right):
                    break
                # Ascend up slope
                slope = -1 if (left > right) else 1
                # Break if we stepped over a peak (switched directions)
                if direction is None:
                    direction = slope
                if direction != slope:
                    break
                # Break if stepping would take us outside of transit
                next_ts = ts + (direction * step)
                if (next_ts < self.start) or (next_ts > self.end):
                    break
                # Step towards the peak
                ts = next_ts
        return self.at(ts)

    # Generator that returns an observation every 'step' seconds
    def points(self, step=15.0):
        # Number of steps that fit within this pass
        count = int(self.duration() / step)
        # Center the observations over the interval
        offset = (self.duration() - (count * step))/2
        for i in range(0, count):
            yield self.at(self.start + offset + (i * step))

    def duration(self):
        return self.end - self.start

    def at(self, t):
        if self.start <= t <= self.end:
            return self.engine.observe(t)
        else:
            raise LookupError("time %f outside of transit window [%f, %f]" % (t, self.start, self.end))

    def __str__(self):
        return str((self.start, self.end, self.peak()['elevation'], self.duration()))