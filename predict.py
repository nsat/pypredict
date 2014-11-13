import time
import urllib2
from datetime import datetime

# Pythonic?  Pickup quick_predict and quick_find from c extension and expose them.
from cpredict import *

def tle(norad_id):
	res = urllib2.urlopen("http://tle.nanosatisfi.com/%s" % str(norad_id))
	if res.getcode() != 200:
		raise Exception("Unable to retrieve TLE from tle.nanosatisfi.com. HTTP code(%s)", res.getcode())
	return res.read().rstrip()

class Observer():
	def __init__(self, tle, qth = None):
		self.tle = tle.rstrip().split('\n')
		self.qth = qth

	def observe(self, at = time.time()):
		if self.qth:
			return quick_find(self.tle, at, self.qth)
		else:
			return quick_find(self.tle, at)

	def passes(self, at = time.time()):
		if self.qth:
			return PassGenerator(self.tle, at, self.qth)
		else:
			return PassGenerator(self.tle, at)

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
	def __init__(self, tle, ts = None, qth = None):
		self.tle  = tle
		self.time = ts or time.time()
		self.qth  = qth

	def __iter__(self):
		return self

	def next(self):
		#print(self.time)
		if self.qth:
			p = Transit(quick_predict(self.tle, self.time, self.qth))
		else:
			p = Transit(quick_predict(self.tle, self.time))
		self.time = p[-1]['epoch'] + 60	#TODO: Hack, need to advance past end of previous pass.  Lower numbers unreliable.
		return p