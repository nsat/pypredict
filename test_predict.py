import predict

TLE = (
    "0 ISS (ZARYA)\n"
    "1 25544U 98067A   23096.18845088  .00017407  00000-0  31715-3 0  9991\n"
    "2 25544  51.6431 325.2993 0006862 159.1562 289.0392 15.49543408390622"
)
QTH = (0.033889, 51.066389, 0.0)  # Macapa, Brazil
T1_IN_TRANSIT = 1680782200        # 2023-04-06T11:56:40Z
T2_NOT_IN_TRANSIT = 1680783900    # 2023-04-06T12:25:00Z


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
