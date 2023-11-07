from datetime import datetime
import random
from typing import List, Union

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
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
    def __init__(self, events: List[Union[Event, str]]=None):
        self.catalog = []
        if events:
            self.add_events(events)

    def add_events(self, events: List[Union[Event, str]]):
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
        mags, lat_err, lon_err, z_err, time, gap = [], [], [], [], [], []
        n, rms = [], []
        for ev in self.catalog:
            mags.append(ev.mag)
            lat_err.append(ev.lat_err)
            lon_err.append(ev.lon_err)
            z_err.append(ev.z_err)
            gap.append(ev.gap)
            rms.append(ev.rms)
            n.append(ev.n)

        print(f"{len(mags)} Total events in the catalog.")
        print("Mean values in catalog:")
        print(f"{'Magnitude': <20} {round(np.mean(np.array(mags)),1)}")
        print(f"{'Lat Error': <20} {round(np.mean(np.array(lat_err)),2)}")
        print(f"{'Lon Error': <20} {round(np.mean(np.array(lon_err)),2)}")
        print(f"{'Depth Error': <20} {round(np.mean(np.array(z_err)),2)}")
        print(f"{'Az. Gap': <20} {round(np.mean(np.array(gap)),2)}")
        print(f"{'RMS': <20} {round(np.mean(np.array(rms)),2)}")
        print(f"{'Num Stations': <20} {round(np.mean(np.array(n)),0)}")
            
    def ttime_plot(self, sep_phase: bool =True, best_fit: bool =False, 
                   phase_list: List =['P',"Pg","Pn","Pb",'S',"Sg","Sn","Sb"],
                   outfile: str =None):
        """
        Generate a travel time plot for the entire catalog.
        :param phase_list: list of phases to gather from Event.ttimes
        :type phase_list: List[str]
        :param sep_phase: Plot different phases in different colors
        :type sep_phase: bool
        :param best_fit: Not implemented yet
        :type best_fit: bool
        :param outfile: Filename to save figure
        :type outfile: str
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

    def filter(self, min_date: Union[datetime,str], 
               max_date: Union[datetime,str]):
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

    def map(self, extent: List[float] =None, buffer: float =0, 
            projection: ccrs.Projection =ccrs.Mercator(), outfile: str =None):
        """ 
        Create a map of event locations. Color events by their ev_id types
        :param extent: map boundaries. [min_lon, max_lon, min_lat, max_lat]. If
            no extent provided, get the extent from the station coordinates.
        :type extent: List
        :param buffer: Distance in degrees to add to the plot borders. Useful 
            when extent is None.
        :type buffer: float
        :param projection: Cartopy projection to use.
        :type projection: cartopy.crs.Projection
        :param outfile: Filename to save image. If None, show the image instead.
        :type outfile: str
        """

        # Get coords of all events
        lats, lons, ev_type, mag = [], [],[], []
        for ev in self.catalog:
            lats.append(ev.latitude)
            lons.append(ev.longitude)
            mag.append(5**ev.mag)        
        # Set coordinates for map extent if extent not explicitly set
        # and add a quarter degree buffer
        if not extent:
            min_lon = min(lons) - buffer
            max_lon = max(lons) + buffer
            min_lat = min(lats) - buffer
            max_lat = max(lats) + buffer
            extent = [min_lon, max_lon, min_lat, max_lat]
        
        fig = plt.figure()
        #ax = fig.add_axes([0, 0, 1, 1], projection=projection)
        ax = plt.axes(projection=projection)
        ax.set_extent(extent, ccrs.Geodetic())
        ax.add_feature(cfeature.STATES.with_scale('10m'), linewidth=0.75,
                      edgecolor='k', facecolor='whitesmoke')
        ax.add_feature(cfeature.LAKES)
        ax.add_feature(cfeature.OCEAN)
        ax.patch.set_visible = False

        cmap = cm.get_cmap('viridis')
        #for i,v in enumerate(lats):
        ax.scatter(lons, lats, marker="o", c='red',
            s=mag,
            linestyle='-', edgecolor='k', alpha=0.75, zorder=10,
            transform=ccrs.Geodetic())

        if outfile:
            plt.savefig(outfile)
        else:
            plt.show() 

    def __len__(self):
        return len(self.catalog)

    def __iter__(self):
        return self.catalog.__iter__()

    def __repr__(self):
        return f"Catalog of {len(self.catalog)} events"

if __name__ == "__main__":
    cat = Catalog(["tests/Sfiles/01-1300-32L.S202204", "tests/Sfiles/01-1544-40L.S201908",
                  "tests/Sfiles/25-1500-14L.S201610", "tests/Sfiles/13-0031-00L.S201906"])
    cat.describe()