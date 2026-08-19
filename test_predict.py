import predict
import pytest

from cpredict import PredictException

TLE = (
    "0 ISS (ZARYA)\n"
    "1 25544U 98067A   23096.18845088  .00017407  00000-0  31715-3 0  9991\n"
    "2 25544  51.6431 325.2993 0006862 159.1562 289.0392 15.49543408390622"
)

OMM = {
    "OBJECT_NAME": "ISS (ZARYA)",
    "OBJECT_ID": "1998-067A",
    "EPOCH": "2026-08-19T03:31:32.932416",
    "MEAN_MOTION": 15.49503867,
    "ECCENTRICITY": 0.00076624,
    "INCLINATION": 51.6332,
    "RA_OF_ASC_NODE": 348.4866,
    "ARG_OF_PERICENTER": 61.8697,
    "MEAN_ANOMALY": 298.3065,
    "EPHEMERIS_TYPE": 0,
    "CLASSIFICATION_TYPE": "U",
    "NORAD_CAT_ID": 25544,
    "ELEMENT_SET_NO": 999,
    "REV_AT_EPOCH": 58151,
    "BSTAR": 0.00019587255,
    "MEAN_MOTION_DOT": 0.00010553,
    "MEAN_MOTION_DDOT": 0,
}

QTH = (0.033889, 51.066389, 0.0)  # Macapa, Brazil
T1_IN_TRANSIT = 1680782200  # 2023-04-06T11:56:40Z
T2_NOT_IN_TRANSIT = 1680783900  # 2023-04-06T12:25:00Z

T1_WITHIN_A_YEAR = 1680782200  # 2023-04-06T11:56:40Z
T2_AFTER_A_YEAR = 1713897435  # 2024-04-23T18:37:15Z

OMM_T1_WITHIN_A_YEAR = 1787153641  # 2026-08-19T15:34:01Z
OMM_T2_AFTER_A_YEAR = 1887153641  # 2029-10-20T01:20:41Z


def test_transits_are_truncated_if_the_overlap_the_start_or_end_times():
    tle = predict.massage_tle(TLE)
    qth = predict.massage_qth(QTH)

    at = T1_IN_TRANSIT
    obs = predict.observe(tle, qth, at=at)
    assert obs["elevation"] > 0

    at = T2_NOT_IN_TRANSIT
    obs = predict.observe(tle, qth, at=at)
    assert obs["elevation"] < 0

    # should not raise a StopIteration
    next(predict.transits(tle, qth, ending_after=at))


def test_predict_of_tle_older_than_a_year():
    # Test a TLE older than a year with a timestamp within a year of its epoch
    # Should not throw an exception
    predict.quick_predict(TLE, T1_WITHIN_A_YEAR, QTH)

    # Test a TLE older than a year with a timestamp outwith a year of its epoch
    # Should raise a PredictException
    with pytest.raises(PredictException) as e_info:
        predict.quick_predict(TLE, T2_AFTER_A_YEAR, QTH)


def test_predict_using_omm():
    # Test running predict using OMM instead of TLE as an input
    # Should not throw an exception
    predict.quick_predict(OMM, OMM_T1_WITHIN_A_YEAR, QTH)

    # Test a OMM older than a year with a timestamp outwith a year of its epoch
    # Should raise a PredictException
    with pytest.raises(PredictException) as e_info:
        predict.quick_predict(OMM, OMM_T2_AFTER_A_YEAR, QTH)
