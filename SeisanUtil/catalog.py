from datetime import datetime
import random
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
                   sep_phase=True, best_fit=False, outfile=None):
        """
        Generate a travel time plot for the entire catalog.
        :param phase_list: list of phases to gather from Event.ttimes
        :type phase_list: List[str]
        """
        times = {}
        for ev in self.catalog:
            if not ev.ttimes:
                ev.calc_ttimes()
            for t in ev.ttimes:
                if t[1] in phase_list:
                    if t[1] in times:
                        times[t[1]] = np.vstack([times[t[1]], 
                                                 np.array([t[2], t[3]])])
                    else:
                        times[t[1]] = np.array([t[2], t[3]])
        fig, ax = plt.subplots()
        phases = times.keys()
        cmap = plt.get_cmap('viridis')
        for i,kv in enumerate(times.items()):
            if sep_phase:
                ax.scatter(kv[1][:,0], kv[1][:,1], 
                    color=cmap.colors[cmap.N//len(phases)*i], alpha=0.75,
                    edgecolors="black", linewidths=0.1, label=kv[0])
            else:
                ax.scatter(kv[1][:,0], kv[1][:,1], color="red", alpha=0.75, 
                   edgecolors="black", linewidth=0.1, label=kv[0])
        ax.set_xlabel("Dist. (km)")
        ax.set_ylabel("Time (s)")
        ax.legend()
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

