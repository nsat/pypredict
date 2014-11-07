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
# Outputs the location of the satellite and related parameters
predict.quick_find(tle, epoch, qth)
# \_ tle - array of strings (lines 0,1,2 of TLE)
# \_ epoch - (optional, defaults: now) number of seconds since epoch (as float)
# \_ qth - (optional, defaults: system) tuple of latitude (float), longitude (float), altitude (int)

# Outputs the next pass of the satellite over the groundstation (throws exception if no pass)
predict.quick_predict(tle, epoch, qth)
# \_ tle - array of strings (lines 0,1,2 of TLE)
# \_ epoch - (optional, defaults: now) number of seconds since epoch (as float)
# \_ qth - (optional, defaults: system) tuple of latitude (float), longitude (float), altitude (int)

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

predict.quick_find(tle.split('\n'), time.time(), (37.7727, 122.407, 25))

predict.quick_predict(tle.split('\n'), time.time(), (37.7727, 122.407, 25))
```