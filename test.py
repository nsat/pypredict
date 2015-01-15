#!/usr/bin/env python

import unittest, time
import predict
from cpredict import quick_find, quick_predict, PredictException

# fetched from http://tle.nanosatisfi.com/40044
TLE = "0 LEMUR 1\n1 40044U 14033AL  15013.74135905  .00002013  00000-0  31503-3 0  6119\n2 40044 097.9584 269.2923 0059425 258.2447 101.2095 14.72707190 30443"
QTH = "fuze-sfgs\n37.7727\n122.4070\n25"
STEP = 15
# T1_IN_TRANSIT is inside the transit that starts after T2_NOT_IN_TRANSIT
T1_IN_TRANSIT     = 1421214440.07
T2_NOT_IN_TRANSIT = 1421202456.13


def transit_to_tuple(transit):
  return (transit.start, transit.duration(), transit.peak(), transit.qth, transit.tle)



class TestPredict(unittest.TestCase):

  def test_transit_prediction_from_within_and_outside_start_time(self):
    tle = predict.massage_tle(TLE)
    qth = predict.massage_qth(QTH.split("\n")[-3:])
    
    at  = T1_IN_TRANSIT
    obs = predict.observe(tle, qth, at=at)
    self.assertTrue(obs['elevation'] > 0)

    t1t = next(predict.transits(tle, qth, ending_after=at))

    at  = T2_NOT_IN_TRANSIT
    obs = predict.observe(tle, qth, at=at)
    self.assertTrue(obs['elevation'] < 0)

    # should not raise a StopIteration
    t2t = next(predict.transits(tle, qth, ending_after=at))
    
    # t1_transit and t2_transit should be the same transit
    self.assertAlmostEqual(t1t.start, t2t.start, delta=1)
    self.assertAlmostEqual(t1t.peak()['elevation'], t2t.peak()['elevation'], delta=0.01)

    # manually construct a transit whose peak is at the end of the transit to verify 
    # transit.peak code is working
    t3t = predict.Transit(tle, qth, t1t.start, t1t.peak()['epoch'])
    self.assertAlmostEqual(t1t.peak()['elevation'], t3t.peak()['elevation'])



if __name__ == '__main__':

  tests = [
    TestPredict
  ]

  for test in tests:
    suite = unittest.TestLoader().loadTestsFromTestCase(test)
    unittest.TextTestRunner(verbosity=2).run(suite)

