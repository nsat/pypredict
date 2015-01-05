PyPredict
=======

Satellite tracking and pass prediction library for Python.

PyPredict is a C Python extension directly adapted from the ubiquitous [predict](http://www.qsl.net/kd2bd/predict.html) satellite tracking tool.
We aim for result-parity and it should produce identical values on the same inputs.

If you think you've found an error, please include predict's differing output in the bug report.
If you think you've found a bug in predict, please report and we'll coordinate with upstream.
### Installation

```bash
sudo apt-get install python-dev
sudo python setup.py install
```

## Usage

PyPredict provides some high level primitives for generating passes along with direct calls to the underlying pass prediction and satellite position calculations.

#### Observe a satellite (relative to a position on earth)

```python
import predict
tle = predict.tle(40044)
o = predict.Observer(tle) # optional (lat, long, alt) argument
o.observe()               # optional time argument defaults to time.time()
# => {
  'altitude': 719.8973016015207,
  'azimuth': 192.95630630260538,
  'decayed': 0,
  'doppler': 932.5572349440811,
  'eclipse_depth': -67.51645147097173,
  'elevation': -53.48611284388438,
  'epoch': 1415903990.986349,
  'footprint': 5794.924485669611,
  'geostationary': 0,
  'has_aos': 1,
  'latitude': -66.68928281112146,
  'longitude': 255.62216756334112,
  'name': '0 LEMUR 1',
  'norad_id': 40044,
  'orbit': 2147,
  'orbital_model': 'SGP4',
  'orbital_phase': 141.91263884508973,
  'orbital_velocity': 26900.11489717512,
  'slant_range': 11076.219591527988,
  'sunlit': 1,
  'visibility': 'D'
 }
```

#### Show upcoming passes of satellite over groundstation

```python
p = o.passes()
for i in range(1,10):
	transit = p.next()
	print("%f\t%f\t%f" % (transit.start, transit.duration(), transit.peak()['elevation']))
```

#### Call predict functions directly

```python
predict.quick_find(tle.split('\n'), time.time(), (37.7727, 122.407, 25))
predict.quick_predict(tle.split('\n'), time.time(), (37.7727, 122.407, 25))
```

##API

<pre>
<b>tle</b>(<i>norad_id</i>)  
        Fetch the TLE for the given NORAD id from the spire tle service.
        Throws a predict.PredictException if tle cannot be loaded.

<b>host_qth</b>()
        Parse and return the host qth file as a (lat(N), long(W), Alt(m)) tuple.
        Throws a predict.PredictException if QTH cannot be loaded and parsed.

<b>Observer</b>(<i>tle[, (lat, long, alt)]</i>)  
    <b>observe</b>(<i>[time]</i>)  
        Return an observation of the satellite via <b>quick_find</b>(<i>tle, time, qth</i>)  
        If <i>time</i> is not defined, it defaults to current time  
    <b>passes</b>(<i>[start, [end]]</i>)  
        Returns iterator of <b>Transit</b>'s that overlap [start, end].
        If <i>start</i> is not defined, it defaults to current time  
        If <i>end</i> is not defined, the iterator will yield passes until the orbit decays  

<b>Transit</b>(<i>tle, qth, start, end</i>)  
    Utility class representing a pass of a satellite over a groundstation.
    Instantiation parameters are parsed and made available as fields.
    <b>points</b>(<i>step=15.0</i>)
        Returns iterator of observations spaced <i>step</i> seconds apart.
    <b>duration</b>()  
        Returns length of transit in seconds
    <b>peak</b>(<i>epsilon=0.1</i>)  
        Returns observation at maximum elevation (+/- ~<i>epsilon</i> seconds)
    <b>at</b>(<i>timestamp</i>)  
        Returns observation from <b>Observer</b>(<i>tle, qth</i>).observe(<i>timestamp</i>)

<b>quick_find</b>(<i>tle[, time[, (lat, long, alt)]]</i>)  
    <i>time</i> defaults to now   
    <i>(lat, long, alt)</i> defaults to values in ~/.predict/predict.qth  
    Returns a dictionary containing:  
        <i>norad_id</i> : NORAD id of satellite.  
        <i>name</i> : name of satellite from first line of TLE.  
        <i>epoch</i> : time of observation in seconds (unix epoch)  
        <i>azimuth</i> : azimuth of satellite in degrees relative to groundstation.  
        <i>altitude</i> : altitude of satellite in degrees relative to groundstation.  
        <i>slant_range</i> : distance to satellite from groundstation in meters.  
        <i>sunlit</i> : 1 if satellite is in sunlight, 0 otherwise.  
        <i>decayed</i>: 1 if satellite has decayed out of orbit, 0 otherwise.  
        <i>geostationary</i> : 1 if satellite is determined to be geostationary, 0 otherwise.  
        <i>latitude</i> : sub-satellite latitude.  
        <i>longitude</i> : sub-satellite longitude.  
        <i>altitude</i> : altitude of satellite relative to sub-satellite latitude, longitude.  
        <i>has_aos</i> : 1 if the satellite will eventually be visible from the groundstation  
        <i>doppler</i> : doppler shift between groundstation and satellite.  
        <i>orbit</i> : refer to predict documentation  
        <i>footprint</i> : refer to predict documentation  
        <i>visibility</i> : refer to predict documentation  
        <i>orbital_model</i> : refer to predict documentation  
        <i>orbital_phase</i> : refer to predict documentation  
        <i>eclipse_depth</i> : refer to predict documentation  
        <i>orbital_velocity</i> : refer to predict documentation  
        
<b>quick_predict</b>(<i>tle[, time[, (lat, long, alt)]]</i>)  
        Returns an array of observations for the next pass as calculated by predict.
        Each observation is identical to that returned by <b>quick_find</b>.
</pre>
