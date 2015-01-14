#!/usr/bin/env python

import unittest, time
import predict
from cpredict import quick_find, quick_predict, PredictException

# fetched from http://tle.nanosatisfi.com/40044
TLE = "0 LEMUR 1\n1 40044U 14033AL  15013.74135905  .00002013  00000-0  31503-3 0  6119\n2 40044 097.9584 269.2923 0059425 258.2447 101.2095 14.72707190 30443"
QTH = "fuze-sfgs\n37.7727\n122.4070\n25"
STEP = 15
T1_IN_TRANSIT     = 1421214440.07
T2_NOT_IN_TRANSIT = 1421202456.13


class TestPredict(unittest.TestCase):

  def test_transits_are_truncated_if_the_overlap_the_start_or_end_times(self):
    #predict.massage_tle(EXAMPLE_QTH)

    tle = predict.massage_tle(TLE)
    qth = predict.massage_qth(QTH)
    
    at  = T1_IN_TRANSIT
    obs = predict.observe(tle, qth, at=at)
    self.assertTrue(obs['elevation'] > 0)

    at  = T2_NOT_IN_TRANSIT
    obs = predict.observe(tle, qth, at=at)
    self.assertTrue(obs['elevation'] < 0)

    # should not raise a StopIteration
    next_transit = next(predict.transits(tle, qth, ending_after=at))
    print next_transit


if __name__ == '__main__':

  tests = [
    TestPredict
  ]

  for test in tests:
    suite = unittest.TestLoader().loadTestsFromTestCase(test)
    unittest.TextTestRunner(verbosity=2).run(suite)