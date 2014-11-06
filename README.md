PyPredict
=======

Satellite tracking and pass prediction library for Python.

PyPredict is a C Python extension directly adapted from the ubiquitous [predict](http://www.qsl.net/kd2bd/predict.html) satellite tracking tool.
We aim for result-parity and it should produce identical values on the same inputs.

If you think you've found an error, please include predict's differing output in the bug report.
If you think you've found a bug in predict, please report and we'll coordinate with upstream.

## Installation
```
sudo python setup.py install
```
## Usage
```
predict.predict(epoch, tle, qth)
# \_ epoch - number of seconds since epoch (as float)
# \_ tle - array of strings (lines 0,1,2 of TLE)
# \_ qth - (optional) tuple of latitude (float), longitude (float), altitude (int)
```
## Example
```
import time
import urllib2
import predict

# Get a TLE
res = urllib2.urlopen("http://tle.nanosatisfi.com/%d" % 40044)
if res.getcode() != 200:
    raise Exception("Unable to retrieve TLE from tle.nanosatisfi.com. HTTP code(%s)", res.getcode())
tle = res.read().rstrip()

predict.predict(time.time(), tle.split('\n'), (37.7727, 122.407, 25))
```