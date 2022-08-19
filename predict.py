import sys
import os
import time

from collections import namedtuple
from copy import copy
from cpredict import PredictException
from cpredict import quick_find as _quick_find
from cpredict import quick_predict as _quick_predict


SolarWindow = namedtuple("SolarWindow", ["start", "end"])


def quick_find(tle, at, qth):
    tle = massage_tle(tle)
    qth = massage_qth(qth)
    return _quick_find(tle, at, qth)


def quick_predict(tle, ts, qth):
    tle = massage_tle(tle)
    qth = massage_qth(qth)
    return _quick_predict(tle, ts, qth)


STR_TYPE = str if sys.version_info.major > 2 else basestring  # noqa: F821


def host_qth(path="~/.predict/predict.qth"):
    path = os.path.abspath(os.path.expanduser(path))
    try:
        with open(path) as qthfile:
            raw = [line.strip() for line in qthfile.readlines()]
            assert len(raw) == 4, "must match:\nname\nlat(N)\nlong(W)\nalt" % path
            return massage_qth(raw[1:])
    except Exception as e:
        raise PredictException("Unable to process qth '%s' (%s)" % (path, e))


def massage_tle(tle):
    try:
        # TLE may or may not have been split into lines already
        if isinstance(tle, STR_TYPE):
            tle = tle.rstrip().split("\n")
        assert len(tle) == 3, "TLE must be 3 lines, not %d: %s" % (len(tle), tle)
        return tle
        # TODO: print a warning if TLE is 'too' old
    except Exception as e:
        raise PredictException(e)


def massage_qth(qth):
    try:
        assert len(qth) == 3, (
            "%s must consist of exactly three elements: (lat(N), long(W), alt(m))" % qth
        )
        return (float(qth[0]), float(qth[1]), int(qth[2]))
    except ValueError as e:
        raise PredictException("Unable to convert '%s' (%s)" % (qth, e))
    except Exception as e:
        raise PredictException(e)


def observe(tle, qth, at=None):
    if at is None:
        at = time.time()
    return quick_find(tle, at, qth)


def transits(tle, qth, ending_after=None, ending_before=None):
    if ending_after is None:
        ending_after = time.time()
    ts = ending_after
    while True:
        transit = quick_predict(tle, ts, qth)
        t = Transit(
            tle,
            qth,
            start=transit[0]["epoch"],
            end=transit[-1]["epoch"],
            _samples=transit,
        )
        if ending_before is not None and t.end > ending_before:
            break
        if t.end > ending_after:
            yield t
        # Need to advance time cursor so predict doesn't yield same pass
        ts = t.end + 60  # seconds seems to be sufficient


def active_transit(tle, qth, at=None):
    if at is None:
        at = time.time()
    transit = quick_predict(tle, at, qth)
    t = Transit(
        tle, qth, start=transit[0]["epoch"], end=transit[-1]["epoch"], _samples=transit
    )
    return t if t.start <= at <= t.end else None


class Transit:
    """A convenience class representing a pass of a satellite over a groundstation."""

    def __init__(self, tle, qth, start, end, _samples=None):
        self.tle = tle
        self.qth = qth
        self.start = start
        self.end = end
        if _samples is None:
            self._samples = []
        else:
            self._samples = [s for s in _samples if start <= s["epoch"] <= end]

    def peak(self, epsilon=0.1):
        """Return observation within epsilon seconds of maximum elevation.

        NOTE: Assumes elevation is strictly monotonic or concave over the [start,end] interval.
        """
        ts = (self.end + self.start) / 2
        step = self.end - self.start
        while step > epsilon:
            step /= 4
            # Ascend the gradient at this step size
            direction = None
            while True:
                mid = observe(self.tle, self.qth, ts)["elevation"]
                left = observe(self.tle, self.qth, ts - step)["elevation"]
                right = observe(self.tle, self.qth, ts + step)["elevation"]
                # Break if we're at a peak
                if left <= mid >= right:
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

    def above(self, elevation, tolerance=0.001):
        """Return portion of transit that lies above argument elevation.

        Elevation at new endpoints will lie between elevation and elevation + tolerance unless
        endpoint of original transit is already above elevation, in which case it won't change, or
        entire transit is below elevation target, in which case resulting transit will have zero
        length.
        """

        def capped_below(elevation, samples):
            """Quick heuristic to filter transits that can't reach target elevation.

            Assumes transit is unimodal and derivative is monotonic. i.e. transit is a smooth
            section of something that has ellipse-like geometry.
            """
            limit = None

            if len(samples) < 3:
                raise ValueError("samples array must have length > 3")

            # Find samples that form a hump
            for i in range(len(samples) - 2):
                a, b, c = samples[i : i + 3]

                ae, be, ce = a["elevation"], b["elevation"], c["elevation"]
                at, bt, ct = a["epoch"], b["epoch"], c["epoch"]

                if ae < be > ce:
                    left_step = bt - at
                    right_step = ct - bt
                    left_slope = (be - ae) / left_step
                    right_slope = (be - ce) / right_step
                    limit = be + max(left_step * right_slope, right_step * left_slope)
                    break

            # If limit isn't set, we didn't find a hump, so max is at one of edges.
            if limit is None:
                limit = max(s["elevation"] for s in samples)

            return limit < elevation

        def add_sample(ts, samples):
            if ts not in [s["epoch"] for s in samples]:
                samples.append(self.at(ts))
                samples.sort(key=lambda s: s["epoch"])

        def interpolate(samples, elevation, tolerance):
            """Interpolate between adjacent samples straddling the elevation target."""

            for i in range(len(samples) - 1):
                a, b = samples[i : i + 2]

                if any(
                    abs(sample["elevation"] - elevation) <= tolerance
                    for sample in [a, b]
                ):
                    continue

                if (a["elevation"] < elevation) != (b["elevation"] < elevation):
                    p = (elevation - a["elevation"]) / (b["elevation"] - a["elevation"])
                    t = a["epoch"] + p * (b["epoch"] - a["epoch"])
                    add_sample(t, samples)
                    return True
            return False

        # math gets unreliable with a real small elevation tolerances (~1e-6), be safe.
        if tolerance < 0.0001:
            raise ValueError("Minimum tolerance of 0.0001")

        # Ensure we've got a well formed set of samples for iterative linear interpolation
        # We'll need at least three (2 needed for interpolating, 3 needed for filtering speedup)
        if self.start == self.end:
            return self
        samples = self._samples[:]
        add_sample(self.start, samples)
        add_sample(self.end, samples)
        if len(samples) < 3:
            add_sample((self.start + self.end) / 2, samples)

        # We need at least one sample point in the sample set above the desired elevation
        protrude = max(samples, key=lambda s: s["elevation"])
        if protrude["elevation"] <= elevation:
            if not capped_below(
                elevation, samples
            ):  # prevent expensive calculation on lost causes
                protrude = self.peak()
                add_sample(
                    protrude["epoch"], samples
                )  # recalculation is wasteful, but this is rare

        if protrude["elevation"] <= elevation:
            start = protrude["epoch"]
            end = protrude["epoch"]
        else:
            # Aim for elevation + (tolerance / 2) +/- (tolerance / 2) to ensure we're >= elevation
            while interpolate(
                samples, elevation + float(tolerance) / 2, float(tolerance) / 2
            ):
                pass
            samples = [s for s in samples if s["elevation"] >= elevation]
            start = samples[0]["epoch"]
            end = samples[-1]["epoch"]
        return Transit(self.tle, self.qth, start, end, samples)

    def prune(self, fx, epsilon=0.1):
        """Return section of a transit where a pruning function is valid.

        Currently used to set elevation threshold, unclear what other uses it might have. fx must
        either return false everywhere or true for a contiguous period including the peak.
        """

        peak = self.peak()["epoch"]
        if not fx(peak):
            start = peak
            end = peak
        else:
            if fx(self.start):
                start = self.start
            else:
                # Invariant is that fx(right) is True
                left, right = self.start, peak
                while (right - left) > epsilon:
                    mid = (left + right) / 2
                    if fx(mid):
                        right = mid
                    else:
                        left = mid
                start = right
            if fx(self.end):
                end = self.end
            else:
                # Invariant is that fx(left) is True
                left, right = peak, self.end
                while (right - left) > epsilon:
                    mid = (left + right) / 2
                    if fx(mid):
                        left = mid
                    else:
                        right = mid
                end = left
        # Use copy to allow subclassing of Transit object
        pruned = copy(self)
        pruned.start = start
        pruned.end = end
        return pruned

    def duration(self):
        return self.end - self.start

    def at(self, t, epsilon=0.001):
        if t < (self.start - epsilon) or t > (self.end + epsilon):
            raise PredictException(
                "time %f outside transit [%f, %f]" % (t, self.start, self.end)
            )
        return observe(self.tle, self.qth, t)


def find_solar_periods(
    start,
    end,
    tle,
    eclipse=False,
    eclipse_depth_threshold=0,
    large_predict_timestep=20,
    small_predict_timestep=1,
):
    """
    Finds all sunlit (or eclipse, if eclipse is set) windows for a tle within a time range.
    """
    qth = (
        0,
        0,
        0,
    )  # doesn't matter since we dont care about relative position from ground

    last_start = None
    ret = []
    prev_period = -1
    t = start
    while t < end:
        obs = observe(tle, qth, t)
        if not eclipse:
            # Check for transitioning into sun, then transitioning out
            if prev_period == 0 and obs["sunlit"] == 1:
                last_start = t
            elif prev_period == 1 and obs["sunlit"] == 0:
                if last_start is not None:
                    ret.append(SolarWindow(last_start, t))
                    last_start = None
        else:
            # Check for transitioning out of sun into eclipse
            if prev_period == 1 and obs["sunlit"] == 0:
                last_start = t
            elif prev_period == 0 and obs["sunlit"] == 1:
                if last_start is not None:
                    ret.append(SolarWindow(last_start, t))
                    last_start = None
        prev_period = obs["sunlit"]
        # Use large steps if not near an eclipse boundary
        if abs(obs["eclipse_depth"]) > eclipse_depth_threshold:
            t += large_predict_timestep
        else:
            t += small_predict_timestep

    return ret
