import predict

TLE = (
    "0 ISS (ZARYA)\n"
    "1 25544U 98067A   22032.20725753  .00005492  00000-0  10513-3 0  9993\n"
    "2 25544  51.6448 289.9951 0006763  85.5907  19.0087 15.49721935324098"
)
QTH = (0.033889, 51.066389, 0.0)  # Macapa, Brazil
T1_IN_TRANSIT = 1643723400  # 2022-02-01T13:50:00Z
T2_NOT_IN_TRANSIT = 1643720700  # 2022-02-01T13:05:00Z


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
