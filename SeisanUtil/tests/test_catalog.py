import os

from SeisanUtil.catalog import Catalog
from SeisanUtil.event import Event
from SeisanUtil.read import read_sfile

def test_catalog():
    ev1 = read_sfile("Sfiles/13-0031-00L.S201906")
    ev2 = "Sfiles/04-1905-10L.S202310"
    cat = Catalog([ev1, ev2])
    assert len(cat) == 2
    for ev in cat:
        assert isinstance(ev, Event)

def test_add_events():
    cat = Catalog()
    ev = read_sfile("Sfiles/13-0031-00L.S201906")
    cat.add_events([ev])
    assert len(cat) == 1

def test_filter_events():
    events = ["Sfiles/01-1300-32L.S202204", "Sfiles/01-1544-40L.S201908",
              "Sfiles/04-1905-10L.S202310", "Sfiles/13-0031-00L.S201906"]
    cat = Catalog(events)
    print(cat)
    # Check time filtering
    minmax_cat = cat.filter(min_date="2022-03-30", max_date="2022-05-20")
    assert len(minmax_cat) == 1
    min_cat = cat.filter(min_date="2022-03-30")
    assert len(min_cat) == 2
    max_cat = cat.filter(max_date="2020-01-01")
    assert len(max_cat) == 2
    # check coordinate filtering
    coord_cat = cat.filter(min_lat=40.8, max_lat=40.9, min_lon=-78.3, max_lon=-78.1)
    assert len(coord_cat) == 1
    lat_cat = cat.filter(min_lat=40.8, max_lat=41.5)
    assert len(lat_cat) == 3
    lon_cat = cat.filter(min_lon=-79.0, max_lon=-78.0)
    assert len(lon_cat) == 3
    

def test_map():
    cat = Catalog(["Sfiles/13-0031-00L.S201906",
                   "Sfiles/02-2325-20L.S202309"])
    cat.map(outfile="Sfiles/tst.png")
    assert os.path.exists("Sfiles/tst.png")
    if os.path.exists("Sfiles/tst.png"):
        os.remove("Sfiles/tst.png")

def test_ttime_plot():
    cat = Catalog(["Sfiles/13-0031-00L.S201906",
                   "Sfiles/02-2325-20L.S202309"])
    cat.ttime_plot(outfile="Sfiles/tst.png")
    assert os.path.exists("Sfiles/tst.png")
    if os.path.exists("Sfiles/tst.png"):
        os.remove("Sfiles/tst.png")

def test_lollipop():
    events = ["Sfiles/01-1300-32L.S202204", "Sfiles/01-1544-40L.S201908",
              "Sfiles/04-1905-10L.S202310", "Sfiles/13-0031-00L.S201906"] 
    cat = Catalog(events)
    cat.lollipop(outfile="Sfiles/tst.png")
    assert os.path.exists("Sfiles/tst.png")
    #if os.path.exists("Sfiles/tst.png"):
    #    os.remove("Sfiles/tst.png")
