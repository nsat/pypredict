import os
import time
import urllib2
from datetime import datetime
from cpredict import quick_find, quick_predict

class PredictException(Exception):
    pass

def tle(norad_id):
    try:
        res = urllib2.urlopen("http://tle.nanosatisfi.com/%s" % str(norad_id))
        if res.getcode() != 200:
            raise urllib2.HTTPError("Unable to retrieve TLE from tle.nanosatisfi.com. HTTP code(%s)" % res.getcode())
        return res.read().rstrip()
    except Exception as e:
        raise PredictException(e)

def qth(qth_path):
    try:
        qth_path = os.path.abspath(os.path.expanduser(qth_path))
        with open(qth_path) as qthfile:
            raw = [l.strip() for l in qthfile.readlines()]
            assert len(raw) == 4, "qth file '%s' must contain exactly 4 lines (name, lat(N), long(W), alt(m))" % qth_path
            # Attempt conversion to format required for predict.quick_find
            return (float(raw[1]), float(raw[2]), int(raw[3]))
    except IOError as e:
        raise PredictException("Unable to open '%s' (%s)" % (qth_path, str(e)))
    except AssertionError as e:
        raise PredictException(str(e))
    except ValueError as e:
        raise PredictException("Unable to process '%s' (%s)" % (qth_path, str(e)))
    except Exception as e:
        raise PredictException(e)

def host_qth():
    return qth("~/.predict/predict.qth")

class Observer():
    def __init__(self, tle, qth=None):
        self.tle = tle.rstrip().split('\n')
        self.qth = qth

    def observe(self, at = time.time()):
        if self.qth:
            return quick_find(self.tle, at, self.qth)
        else:
            return quick_find(self.tle, at)

    def passes(self, at = time.time()):
        return PassGenerator(self.tle, at, self.qth)

# Transit is a thin wrapper around the array of dictionaries returned by cpredict.quick_predict
class Transit():
    def __init__(self, observations):
        self.points = observations

    def start_time(self):
        return self.points[0]['epoch']

    def end_time(self):
        return self.points[-1]['epoch']

    # TODO: Verify quick_predict returns observation at peak of transit
    def max_elevation(self):
        return max([p['elevation'] for p in self.points])

    def __getitem__(self, key):
        return self.points[key]

class PassGenerator():
    def __init__(self, tle, ts=None, qth=None):
        self.tle  = tle
        self.time = ts or time.time()
        self.qth  = qth

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if self.qth:
            p = Transit(quick_predict(self.tle, self.time, self.qth))
        else:
            p = Transit(quick_predict(self.tle, self.time))
        #HACK: If the timestamp passed to quick_predict is within a pass (or within an unclear
        #      delta of one of the endpoints, it will return that pass.  To generate the next
        #      pass, we have to advance the requested time.  It's not clear how much of a buffer
        #      we need, but the following seems to work.  Single-digits amounts weren't enough.
        self.time = p.end_time() + 60
        return p
