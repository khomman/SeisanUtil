from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import numpy as np

from SeisanUtil.event import Event
from SeisanUtil.read import read_sfile


class Catalog:
    """ 
    Catalog class contains a list of Events and methods to process and plot
    the data.
    :param events: Initial list of events to process. Can accept a list of 
        sfile paths and/or Event instances.
    :type events: List[Events/str]
    """
    def __init__(self, events=None):
        self.catalog = []
        if events:
            self.add_events(events)

    def add_events(self, events: List[Event]):
        """
        Appends events to the catalog instance. Accepts a list consiting 
        of sfile paths and/or Event instances
        :param events: List of sfile paths and/or Event instances
        :type events: List[Events/str]    
        """
        for ev in events:
            if isinstance(ev, Event):
                self.catalog.append(ev)
            elif isinstance(ev, str):
                ev = read_sfile(ev)
                self.catalog.append(ev)

    def describe(self):
        """Output basic statistics about the catalog"""
        pass
            
    def ttime_plot(self, phase_list=['P',"Pg","Pn","Pb",'S',"Sg","Sn","Sb"],
                   best_fit=False, outfile=None):
        """
        Generate a travel time plot for the entire catalog.
        :param phase_list: list of phases to gather from Event.ttimes
        :type phase_list: List[str]
        """
        times = []
        for ev in self.catalog:
            if not ev.ttimes:
                ev.calc_ttimes()
            for t in ev.ttimes:
                if t[1] in phase_list:
                    times += [[t[2], t[3]]]
        times = np.array(times)
        fig, ax = plt.subplots()
        ax.scatter(times[:,0], times[:,1], c="red", alpha=0.75, 
                   edgecolors="black", linewidth=0.1)
        ax.set_xlabel("Dist. (km)")
        ax.set_ylabel("Time (s)")
        #ax.set_title(f"Mag. {self.mag} Event on {self.origin_time}")
        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()

    def filter(self, min_date, max_date):
        """ 
        Return new catalog of events within a date range
        :param min_date: Minimum date used for filtering. Either a
                datetime instance or a str with "%Y-%m-%d" format
        :type min_date: datetime | str
        :param max_date: Maximum date used for filtering. Either a 
                datetime instance or a str with "%Y-%m-%d" format
        :type max_date: datetime | str
        :return Event
        """
        if ~isinstance(min_date, datetime):
            min_date = datetime.strptime(min_date, "%Y-%m-%d")
        if ~isinstance(max_date, datetime):
            max_date = datetime.strptime(max_date, "%Y-%m-%d")
        evs = []
        for ev in self.catalog:
            if ev.origin_time.date() <= max_date.date() and \
               ev.origin_time.date() >= min_date.date():
                evs.append(ev)
        return Catalog(evs)
            

    def __len__(self):
        return len(self.catalog)

    def __iter__(self):
        return self.catalog.__iter__()

    def __repr__(self):
        return f"Catalog of {len(self.catalog)} events"


if __name__ == "__main__":
    evs = ["tests/Sfiles/01-1300-32L.S202204",
           "tests/Sfiles/01-1544-40L.S201908",
           "tests/Sfiles/04-1905-10L.S202310",
           "tests/Sfiles/13-0031-00L.S201906"]
    cat = Catalog(evs)
    #cat.ttime_plot(outfile="TTPlot.png")
    ev = read_sfile("tests/Sfiles/01-1300-32L.S202204")
    print(ev.__dir__())