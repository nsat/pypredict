import predict

TLE = (
    "0 ISS (ZARYA)\n"
    "1 25544U 98067A   23096.18845088  .00017407  00000-0  31715-3 0  9991\n"
    "2 25544  51.6431 325.2993 0006862 159.1562 289.0392 15.49543408390622"
)
QTH = (0.033889, 51.066389, 0.0)  # Macapa, Brazil

ENDING_AFTER = 1680782200         # 2023-04-06T11:56:40Z
ENDING_BEFORE = 1681387000        # 2023-04-13T11:56:40Z

MIN_ELEVATION = 10
MIN_DURATION = 1

TRANSITS_REF = [
    {"start": 1680781759.5005624, "end": 1680782160.6740706},
    {"start": 1680823531.4431722, "end": 1680823906.632853},
    {"start": 1680865311.7306323, "end": 1680865657.2993975},
    {"start": 1680907105.8399603, "end": 1680907378.5976427},
    {"start": 1680912921.9732332, "end": 1680913150.2145195},
    {"start": 1680948922.5879023, "end": 1680949089.099553},
    {"start": 1680954640.4831667, "end": 1680954960.0576594},
    {"start": 1680996376.7773402, "end": 1680996737.0890093},
    {"start": 1681038123.311641, "end": 1681038517.6482813},
    {"start": 1681079878.0165846, "end": 1681080275.4995687},
    {"start": 1681121639.6387215, "end": 1681122038.876846},
    {"start": 1681163409.6062121, "end": 1681163779.7993734},
    {"start": 1681205187.1739054, "end": 1681205524.298174},
    {"start": 1681211103.2199135, "end": 1681211196.8242755},
    {"start": 1681246981.065788, "end": 1681247238.721029},
    {"start": 1681252780.5639017, "end": 1681253025.8338327},
    {"start": 1681288803.5887175, "end": 1681288934.4458292},
    {"start": 1681294498.2477252, "end": 1681294827.8092008},
    {"start": 1681336233.208954, "end": 1681336599.2881413},
    {"start": 1681377976.8515246, "end": 1681378373.9713566}
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
