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
    filtered_cat = cat.filter("2022-03-30", "2022-05-20")
    assert len(filtered_cat) == 1