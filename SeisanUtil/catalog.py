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

    def add_events(self, events: List[Union[Event, str]], **kwargs):
        """
        Appends events to the catalog instance. Accepts a list consiting 
        of sfile paths and/or Event instances
        :param events: List of sfile paths and/or Event instances
        :type events: List[Events/str]
        :param **kwargs: Pass additional kwargs to read_sfile
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

    def _filter_date(self, ev: Event, min_date: Union[datetime,str],
                     max_date: Union[datetime, str]):
        """
        Check if an event origin time satisfies the criteria from
        min and max date. Return True if so and False otherwise
        """
        if min_date and ~isinstance(min_date, datetime):
            min_date = datetime.strptime(min_date, "%Y-%m-%d")
        if max_date and ~isinstance(max_date, datetime):
            max_date = datetime.strptime(max_date, "%Y-%m-%d")
        
        if min_date and max_date:
            if ev.origin_time.date() <= max_date.date() and \
                ev.origin_time.date() >= min_date.date():
                return True
        if min_date and not max_date:
            if ev.origin_time.date() >= min_date.date():
                return True
        if max_date and not min_date:
            if ev.origin_time.date() <= max_date.date():
                return True
        return False

    def _filter_coord(self, ev: Event, min_lat: float, max_lat: float,
                      min_lon: float, max_lon: float):
        """ 
        Check if event coordinates are between min and max latitude
        return True if event is within the region, false otherwise
        """
        if min_lat and not max_lat or max_lat and not min_lat:
            raise ValueError("Provide both min_lat and max_lat")

        if min_lon and not max_lon or max_lon and not min_lon:
            raise ValueError("Provide both min_lon and max_lon")

        if min_lat and min_lon:
            if ev.latitude >= min_lat and ev.latitude <= max_lat \
                and ev.longitude >= min_lon and ev.longitude <= max_lon:
                return True
        if min_lat and not min_lon:
            if ev.latitude >= min_lat and ev.latitude <= max_lat:
                return True
        if min_lon and not min_lat:
            if ev.longitude >= min_lon and ev.longitude <= max_lon:
                return True

        return False

    def filter(self, min_date: Union[datetime,str]=None, 
               max_date: Union[datetime,str] =None, min_lat: float =None,
               max_lat: float =None, min_lon: float =None,
               max_lon: float =None):
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
        filt_time = True # if these are true we want to add event
        filt_coord = True # to the filtered catalog
        evs = []
        for ev in self.catalog:
            if any((min_date, max_date)):
               filt_time = self._filter_date(ev, min_date, max_date) 
            if any((min_lat, max_lat, min_lon, max_lon)):
                filt_coord = self._filter_coord(ev, min_lat, max_lat,
                                           min_lon, max_lon)
            if filt_time and filt_coord:
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

    def lollipop(self, outfile=None):
        """ 
        Create lollipop plot of the events with time on the x-axis
        and magnitude on the y-axis.
        :param outfile: Filename to save image to, if None, show the image
        :type outfile: None
        :returns: None
        :rtype: None
        """
        mags, otimes = [], []
        for ev in self.catalog:
            mags.append(ev.mag)
            otimes.append(ev.origin_time)
        sorted_times = [(i,j) for i,j in sorted(zip(otimes,mags))]
        sorted_times = np.array(sorted_times)
        fig, ax = plt.subplots()
        markerlines, stemlines, baseline = ax.stem(sorted_times[:,0],
                                                   sorted_times[:,1],
                                                   linefmt="k-",
                                                   markerfmt="ro")
        markerlines.set_markeredgecolor('dimgrey')
        markerlines.set_markeredgewidth(0.5)
        markerlines.set(alpha=0.75)
        stemlines.set_color('dimgrey')
        baseline.set_color('black')
        #ax.tick_params(axis='x', labelrotation=45)
        ax.set_xlabel("Date")
        ax.set_ylabel("Magnitude")
        fig.autofmt_xdate()
        fig.tight_layout()

        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()

    def mag_complete(self,):
        pass

    def __len__(self):
        return len(self.catalog)

    def __iter__(self):
        return self.catalog.__iter__()

    def __repr__(self):
        return f"Catalog of {len(self.catalog)} events"
