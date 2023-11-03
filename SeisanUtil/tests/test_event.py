import datetime
import os

import pytest

from SeisanUtil.event import Event
from SeisanUtil.read import read_sfile


def test_event():
    event = Event()
    assert isinstance(event, Event)
    event = Event(depth=10.2, gap=182, rms=0.5832)
    assert event.depth == 10.2
    assert event.gap == 182
    assert event.origin_time == None

def test_update_from_dict():
    event = Event()
    event.update_from_dict({'latitude': 1.234, 'longitude': -77.2381})
    assert event.latitude == 1.234
    assert event.longitude == -77.2381

def test_sta_coords():
    event = Event()
    sta_coords = {"sta1":[21.2, 33.3],"sta2": [-55.5, -123.333]}
    event.add_station_coords(sta_coords, arrivals_only=False)
    assert event.sta_coords == sta_coords

    # No arrivals in instance should raise value error if arrivals_only flag
    # set to true
    with pytest.raises(ValueError):
        event.add_station_coords(sta_coords, arrivals_only=True)

def test_add_arrivals_from_dict():
    event = Event()
    arrivals = [{'sta': 'ZEL1', 'inst': '', 'cmp': '2', 'qual': 'E', 
                 'phase': 'P', 'wgtind': '0', 'pol': '', 'arr_h': 19, 
                 'arr_m': 5, 'arr_s': 17.36, 'amp': '', 'per': '', 'ain': 90.0,
                 'tres': -0.19, 'dist': 31.0, 'az': 348.0, 
                 'arrtime': datetime.datetime(2023, 10, 4, 19, 5, 17, 360000)},
                 {'sta': 'IUPA', 'inst': 'H', 'cmp': 'N', 'qual': '', 
                 'phase': 'IAML', 'wgtind': '', 'pol': '', 'arr_h': 19, 
                 'arr_m': 5, 'arr_s': 30.78, 'amp': 169.4, 'per': 0.8, 
                 'ain': '', 'tres': '', 'dist': '', 'az': '', 
                 'arrtime': datetime.datetime(2023, 10, 4, 19, 5, 30, 780000)}
                 ]
    event.add_arrivals_from_dict(arrivals[0])
    event.add_arrivals_from_dict(arrivals[1])
    assert event.phase_arrivals[0] == arrivals[0]
    assert event.amplitudes[0] == arrivals[1]

def test_ttimes():
    event = Event()
    origin_time = datetime.datetime(2023, 10, 5, 20, 00, 00, 000000)
    arr_time_1 = datetime.datetime(2023, 10, 5, 20, 00, 5, 000000)
    arr_time_2 = datetime.datetime(2023, 10, 5, 20, 00, 7, 500000)
    event.origin_time = origin_time
    event.phase_arrivals = [{"sta": "sta1", "phase": "P", "dist": 10,
                            "arrtime": arr_time_1}, 
                            {"sta": "sta2", "phase": "P", "dist": 10,
                            "arrtime": arr_time_2}]
    times = event.calc_ttimes()
    assert times[0] == ["sta1", "P", 10, 5.0]
    assert times[1] == ["sta2", "P", 10, 7.5]

def test_ttime_plot():
    """Just make sure it runs, we aren't comparing images"""
    event = read_sfile("Sfiles/13-0031-00L.S201906")
    event.ttime_plot(outfile="Sfiles/tst.png", phase_list=['P'])
    assert os.path.exists("Sfiles/tst.png")
    if os.path.exists("Sfiles/tst.png"):
        os.remove("Sfiles/tst.png")
    event.ttime_plot(outfile="Sfiles/tst.png")
    assert os.path.exists("Sfiles/tst.png")
    if os.path.exists("Sfiles/tst.png"):
        os.remove("Sfiles/tst.png")

def test_ttime_map():
    event = read_sfile("Sfiles/13-0031-00L.S201906")
    with pytest.raises(ValueError):
        event.ttime_map(outfile="Sfiles/tst.png", phase_list=['P'])

    sta_coords = {}
    with open('Sfiles/staCoords.txt', 'r') as f:
        for line in f.readlines():
            sta, lat, lon = line.split()
            sta_coords[sta] = [lat,lon]
    event.add_station_coords(sta_coords)
    event.ttime_map(outfile="Sfiles/tst.png", phase_list=["P"])
    assert os.path.exists("Sfiles/tst.png")
    if os.path.exists("Sfiles/tst.png"):
        os.remove("Sfiles/tst.png")
    event.ttime_map(outfile="Sfiles/tst.png")
    assert os.path.exists("Sfiles/tst.png")
    if os.path.exists("Sfiles/tst.png"):
        os.remove("Sfiles/tst.png")