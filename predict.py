import time
from cpredict import quick_find, quick_predict, PredictException

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
        assert len(qth) == 3, "%s must consist of exactly three elements: (lat(N), long(W), alt(m))" % qth
        return (float(qth[0]), float(qth[1]), int(qth[2]))
    except ValueError as e:
        raise PredictException("Unable to convert '%s' (%s)" % (qth, str(e)))
    except Exception as e:
        raise PredictException(e)

def observe(tle, qth, at=None):
    tle = massage_tle(tle)
    qth = massage_qth(qth)
    if at is None:
        at = time.time()
    return quick_find(tle, at, qth)

def transits(tle, qth, ending_after=None, ending_before=None):
    tle = massage_tle(tle)
    qth = massage_qth(qth)
    if ending_after is None:
        ending_after = time.time()
    ts = ending_after
    while True:
        transit = quick_predict(tle, ts, qth)
        t = Transit(tle, qth, start=transit[0]['epoch'], end=transit[-1]['epoch'])
        if (ending_before != None and t.end > ending_before):
            break
        if (t.end > ending_after):
            yield t
        # Need to advance time cursor so predict doesn't yield same pass
        ts = t.end + 60     #seconds seems to be sufficient

# Transit is a convenience class representing a pass of a satellite over a groundstation.
class Transit():
    def __init__(self, tle, qth, start, end):
        self.tle = massage_tle(tle)
        self.qth = massage_qth(qth)
        self.start = start
        self.end = end

    # return observation within epsilon seconds of maximum elevation
    # NOTE: Assumes elevation is strictly monotonic or concave over the [start,end] interval
    def peak(self, epsilon=0.1):
        ts =  (self.end + self.start)/2
        step = (self.end - self.start)
        while (step > epsilon):
            step /= 4
            # Ascend the gradient at this step size
            direction = None
            while True:
                mid   = observe(self.tle, self.qth, ts)['elevation']
                left  = observe(self.tle, self.qth, ts - step)['elevation']
                right = observe(self.tle, self.qth, ts + step)['elevation']
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

    def duration(self):
        return self.end - self.start

    def at(self, t):
        if t < self.start or t > self.end:
            raise PredictException("time %f outside transit [%f, %f]" % (t, self.start, self.end))
        return observe(self.tle, self.qth, t)
        