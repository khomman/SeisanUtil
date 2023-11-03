from SeisanUtil.event import Event
import SeisanUtil.read as sur

def test_read_event():
    ev1 = sur.read_sfile("Sfiles/01-1544-40L.S201908")
    ev2 = sur.read_sfile("Sfiles/13-0031-00L.S201906")

    assert type(ev1) == Event
    assert type(ev2) == Event

def test_parse_type_1():
    type_1_line = " 1996  6 3 1955 35.5 D  47.760 153.227  0.0  TES 12 1.1         5.6WHRV 5.6bPDE1"
    info = sur._parse_type_1(type_1_line)
    assert info["year"] == 1996
    assert info["month"] == 6
    assert info["day"] == 3
    assert info["latitude"] == 47.760
    assert info["longitude"] == 153.227
    assert info["depth"] == 0.0
    assert info['n'] == 12
    assert info["rms"] == 1.1

def test_parse_type_2():
    pass

def test_parse_type_3():
    type_3_line = " This is a comment line                                                         "
    com_line = sur._parse_type_3(type_3_line)["comment"]
    assert com_line.strip() == "This is a comment line"

def test_parse_type_4():
    pass

def test_parse_type_5():
    pass

def test_parse_type_phase_nordic():
    nordic = " TRO  SZ EP       20 5 32.5                               21    1.7510 6471 343 "
    info = sur._parse_type_phase_nordic(nordic)
    assert info["sta"] == "TRO"
    assert info["phase"] == "P"
    assert info["arr_h"] == 20
    assert info["arr_m"] == 5 
    assert info["arr_s"] == 32.5
    assert info["ain"] == 21.0
    assert info["tres"] == 1.75
    assert info["dist"] == 6471.0
    assert info["az"] == 343.0

def test_parse_type_phase_nordic2():
    pass

def test_parse_type_6():
    type_6 = " 1996-06-03-2002-18S.TEST__012                                                 6"
    assert sur._parse_type_6(type_6)["wf_location"] == "1996-06-03-2002-18S.TEST__012"

def test_parse_type_E():
    type_E = " GAP=348        2.88     999.9   999.9999.9 -0.1404E+08 -0.3810E+08  0.1205E+09E"
    info = sur._parse_type_E(type_E)
    assert info["gap"] == 348
    assert info["lat_err"] == 999.9
    assert info["lon_err"] == 999.9
    assert info["otime_err"] == 2.88
    assert info["z_err"] == 999.9

def test_parse_type_F():
    type_F = "      93.2      74.8     -48.2     2                                           F"
    info = sur._parse_type_F(type_F)
    assert info["sdr_aki"].strip() == "93.2      74.8     -48.2"
    