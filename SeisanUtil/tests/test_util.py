import os

import SeisanUtil.util as suu

def test_read_station_coords():
    coords = suu.read_station_coords("Sfiles/staCoords.txt")
    assert coords["ALLY"] == [41.6492, -80.1448]
    assert coords["KSPA"] == [41.557, -75.7682]

    # Build a csv and test the other args
    with open("Sfiles/tmpStaTest.csv", "w") as f:
        f.write("Some,Junk,STA1,More,13.332,JUNK,101.55\n")
        f.write("Some, Junk,   STA2, More, -13.333, stuff, -94.99\n")
    
    coords = suu.read_station_coords("Sfiles/tmpStaTest.csv",
                                     delim=",", sta_col=3, lat_col=5, lon_col=7)
    assert coords["STA1"] == [13.332, 101.55]
    assert coords["STA2"] == [-13.333, -94.99]
    if os.path.exists("Sfiles/tmpStaTest.csv"):
        os.remove("Sfiles/tmpStaTest.csv")

def test_calc_dist():
    assert round(suu.calc_dist([5,2], [8, 12]),2) == 1160.02

def test_least_squares_bf():
    line, slope, b = suu.least_squares_bf([1,2,3], [4,1,1])
    assert slope == -1.5
    assert b == 5.0
    assert line[0] == 3.5
    assert line[-1] == 0.5