import predict

TLE = (
    "0 ISS (ZARYA)\n"
    "1 25544U 98067A   22032.20725753  .00005492  00000-0  10513-3 0  9993\n"
    "2 25544  51.6448 289.9951 0006763  85.5907  19.0087 15.49721935324098"
)
QTH = (0.033889, 51.066389, 0.0)  # Macapa, Brazil

ENDING_AFTER = 1643720700  # 2022-02-01T13:05:00Z
ENDING_BEFORE = 1644325500  # 2022-02-08T13:05:00Z

MIN_ELEVATION = 10
MIN_DURATION = 1

TRANSITS_REF = [
    {"start": 1643723116.22434, "end": 1643723516.987234},
    {"start": 1643764874.083364, "end": 1643765265.3938956},
    {"start": 1643806649.5753431, "end": 1643807015.1396928},
    {"start": 1643848426.4339318, "end": 1643848743.1023502},
    {"start": 1643854302.3515873, "end": 1643854454.722202},
    {"start": 1643890227.7005908, "end": 1643890465.3432565},
    {"start": 1643896002.9880626, "end": 1643896277.0759523},
    {"start": 1643937721.9717846, "end": 1643938061.8765898},
    {"start": 1643979464.7059774, "end": 1643979842.7585597},
    {"start": 1644021207.4925222, "end": 1644021604.0888827},
    {"start": 1644062967.0657983, "end": 1644063368.0047994},
    {"start": 1644104726.0510883, "end": 1644105112.630568},
    {"start": 1644146501.024817, "end": 1644146860.137256},
    {"start": 1644188280.245481, "end": 1644188583.2041698},
    {"start": 1644194133.3048844, "end": 1644194316.9549828},
    {"start": 1644230083.899797, "end": 1644230299.963708},
    {"start": 1644235839.9425225, "end": 1644236130.7524247},
    {"start": 1644277562.037712, "end": 1644277910.0568247},
    {"start": 1644319304.5025349, "end": 1644319688.5155852},
]

TOLERANCE = 0.1


def test_transits_above():
    tle = predict.massage_tle(TLE)
    qth = predict.massage_qth(QTH)

    transits = predict.transits(
        tle, qth, ending_after=ENDING_AFTER, ending_before=ENDING_BEFORE
    )
    transits = [t.above(MIN_ELEVATION) for t in transits]
    transits = [t for t in transits if t.duration() > MIN_DURATION]
    transits = [{"start": t.start, "end": t.end} for t in transits]

    assert len(transits) == len(TRANSITS_REF)

    test_ok = True
    for i, t in enumerate(TRANSITS_REF):
        if (
            transits[i]["start"] < t["start"] - TOLERANCE
            or t["start"] + TOLERANCE < transits[i]["start"]
        ):
            test_ok = False
        if (
            transits[i]["end"] < t["end"] - TOLERANCE
            or t["end"] + TOLERANCE < transits[i]["end"]
        ):
            test_ok = False

    assert test_ok
