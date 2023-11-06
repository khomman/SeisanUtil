from datetime import datetime
import os
import random

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
import numpy as np

from SeisanUtil.util import least_squares, calc_dist

class Event:
    """ 
    An object to hold information about a seismic event. 
    :param origin_time: Datetime object of the origin time for the seismic event
    :type origin_time: Datetime.Datetime
    :param latitude: Latitude of the hypocenter
    :type latitude: float
    :param longitude: Longitude of the hypocenter
    :type longitude: float
    :param depth: Depth of hypocenter in km
    :type depth: float
    :param fixed_depth: Was the depth fixed in the location algorithm
    :type fixed_depth: bool
    :param mag: magnitude for the seismic event
    :type mag: float
    :param lat_err: Latitude error (in km) for the seismic event
    :type lat_err: float
    :param lon_err: Longitude error (in km) for the seismic event
    :type lon_err: float
    :param otime_err: Error in origin time (s) for the seismic event
    :type otime_err: float
    :param z_err: Vertical error for the seismic event (in km)
    :type z_err: float
    :param n: Number of stations used to locate seismic event
    :type n: int
    :param gap: Aziumuthal gap from the location algorithm
    :type gap: float
    :param rms: Root-mean-square value from the location algorithm
    :type rms: float
    :param ev_type: Event type identifier
    :type ev_type: str
    :param sta_coords: Station coordinates used in this event location. 
            Dictionary with station name as keys and [Lat, Lon] as values.
            sta_coords = {"sta1": [lat1,lon1], "sta2": [lat2,lon2]}
    :type sta_coords: dict
    """
    def __init__(self, origin_time=None, latitude=None, longitude=None,
                 depth=None, fixed_depth=False, mag=None, lat_err=None, 
                 lon_err=None, z_err=None, otime_err=None, n=None, gap=None, 
                 rms=None, ev_type=None, sta_coords=None):
        self.origin_time = origin_time
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth
        self.mag = mag 
        self.lat_err = lat_err
        self.lon_err = lon_err
        self.z_err = z_err
        self.otime_err = otime_err
        self.n = n
        self.gap = gap
        self.fixed_depth = fixed_depth
        self.rms = rms
        self.ev_type = ev_type
        self.phase_arrivals = []
        self.ttimes = []
        self.amplitudes = []
        if sta_coords:
            self.sta_coords = sta_coords
        else:
            self.sta_coords = []

    def update_from_dict(self, d):
        """
        Update the event instance from a dictionary. Sets all dict keys to 
        method attributes.
        :param d: Dictionary of new attributes
                d = {"depth": 5.4, "mag": 4.2, "rms": 0.3281}
        :type d: dict
        """
        for k,v in d.items():
            setattr(self, k, v)
    
    def add_arrivals_from_dict(self, d):
        """
        Add dictionary to an arrival information list for the event instance. 
        If key "amp" exists in dictionary and evaluates to True then the dict
        is added as an amplitude (ev.amplitudes), otherwise it is added
        as a phase arrival (ev.phase_arrivals).
        :param d: Dictionary containing information about an arrival
        :type d: Dict 
        """
        # separate phase and amplitude arrivals
        if "amp" in d and d["amp"]:
            self.amplitudes.append(d)
        else:
            self.phase_arrivals.append(d)

    def add_station_coords(self, sta_coords, arrivals_only=True):
        """ Add dict of station coordinates as an attribute to the instance.
        Ex:
            sta_coords = {sta1: [lat1, lon1], sta2: [lat2, lon2]}
        :param sta_coords: Station coordinate dictionary to add
        :type sta_coords: dict
        :param arrivals_only: If True, only add stations that have an associated
                arrival in ev.phase_arrivals or ev.amplitudes
        :type arrivals_only: bool
        """
        if arrivals_only:
            if not self.phase_arrivals and not self.amplitudes:
                raise ValueError("No phases in this instance.  Run with"
                                  " arrivals_only set to False")
            stations = [arr["sta"] for arr in self.phase_arrivals]
            stations += [arr["sta"] for arr in self.amplitudes]
            stations = list(set(stations))
            coords = {}
            for sta in stations:
                lat, lon = float(sta_coords[sta][0]), float(sta_coords[sta][1])
                coords[sta] = [lat, lon]
            self.sta_coords = coords
        else:
            self.sta_coords = sta_coords
        
    
    def _kim(self, sta_coords=None, cmp_combine='max', netmag_type='mean',
             min_dist=100, max_dist=800):
        """ 
        Magnitude function for eastern U.S from Kim (1998; "ML in Eastern
        North America").
        :param sta_coords: Dictionary of station coordinates. See
            Event.add_station_coords.
        :type sta_coords: dict
        :param cmp_combine: How to combine amplitude measurements from multiple
            components. Can use "mean" or "max".
        :type cmp_combine: str
        :param netmag_type: How to calculate the network magnitude from
            individual station magnitudes. Can use "median" or "mean".
        :type netmag_type: str
        :param min_dist: minimum distance required to calculate a magnitude.
            Kim's equation is originally defined from 100 - 800 km.
        :type min_dist: int
        :param max_dist: maximum distance required to calculate a magnitude.
            Kim's equation is originally defined from 100 - 800 km.
        :type max_dist: int
        :return: network magnitude (ML)
        :rtype: float
        """
        # Station magnitudes
        if not self.sta_coords:
            if sta_coords:
                self.add_station_coords(sta_coords)
            else:
                raise ValueError("Event does not contain sta_coords.")
        sta_mags = {}
        for amp in self.amplitudes:
            sta = amp["sta"]
            print(self.longitude, self.latitude)
            print(sta, self.sta_coords[sta][1], self.sta_coords[sta][0])
            sta_dist = calc_dist([self.sta_coords[sta][0], self.sta_coords[sta][1]],
                                 [self.latitude, self.longitude])
            print(sta, sta_dist)
            mag = np.log10(amp["amp"]/1000.0)+(1.55*np.log10(sta_dist))-0.22
            if sta in sta_mags:
                sta_mags[sta].append(mag)
            else:
                sta_mags[sta] = [mag]
        if netmag_type == 'median':
            net_mag = round(np.median([max(v) for k,v in sta_mags.items()]),1)
        else:
            net_mag = round(np.mean([max(v) for k,v in sta_mags.items()]),1)
        return net_mag


    def calc_mag(self, func=_kim, **kwargs):
        """ 
        By default, we read mag from the seisan Sfile.  This function will
        update self.mag by calculating the magnitude using a defined function. 
        If no function is provided, defaults to ML magnitude formula from 
        Kim (1998) for eastern U.S.
        :param func: Function use to calculate a magnitude
        :type: function
        :param **kwargs: Additional keyword arguments are passed to the
            function defined by func.
         
        """
        if func.__name__ == "_kim":
            self.mag = func(self, **kwargs)
        else:
            self.mag = func(**kwargs)

    def calc_ttimes(self):
        """ 
        Calculate travel times for all phase arrivals in this instance
        :return: Array of travel times
        :rtype: List
        """
        for arr in self.phase_arrivals:
            # Phases not in the seisan config files may not have a 
            # distance param but are still in the Sfile and just not used in 
            # the location. Skip them
            if not arr["dist"]:
                continue
            ttime = (arr["arrtime"] - self.origin_time).total_seconds()
            self.ttimes.append([arr['sta'], arr['phase'], arr['dist'], ttime])
        return self.ttimes

    def ttime_plot(self, phase_list=['P',"Pg","Pn","Pb",'S',"Sg","Sn","Sb"],
                   sep_phase=True, outfile=None):
        """
        Create a travel time plot for this event.
        :param phase_list: List of all phase identifiers to use in generating
            the plot
        :type phase_list: List
        :param outfile: Filename to save the figure. If none provide, will show
            using matplotlib.show()
        :type outfile: str
        """
        if not self.ttimes:
            self.calc_ttimes()
        times = {}
        for t in self.ttimes:
            if t[1] in phase_list:
                if t[1] in times:
                    times[t[1]] = np.vstack([times[t[1]], 
                                             np.array([t[2], t[3]])])
                else:
                    times[t[1]] = np.array([t[2], t[3]])
        
        fig, ax = plt.subplots()
        phases = times.keys()
        cmap = plt.get_cmap('viridis')
        colors = random.sample(cmap.colors, len(phases))
        for i,kv in enumerate(times.items()):
            if sep_phase:
                ax.scatter(kv[1][:,0], kv[1][:,1],
                color=cmap.colors[cmap.N//len(phases)*i], alpha=0.75, 
                edgecolors="black", linewidth=0.1, label=kv[0])
            else:
                ax.scatter(kv[1][:,0], kv[1][:,1], color="red", alpha=0.75,
                edgecolors='black', linewidths=0.1, label=kv[0])
        ax.set_xlabel("Dist. (km)")
        ax.set_ylabel("Time (s)")
        ax.set_title(f"Mag. {self.mag} Event on {self.origin_time}")
        ax.legend()
        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()
    
    def ttime_map(self, extent=None, buffer=0, sta_coords=None, 
                  phase_list=['P'], projection=ccrs.Mercator(), 
                  max_duration=None, outfile=None):
        """ 
        Create a map of event location, station location. Color stations
        by arrival time of phase in phase_list. Station locations need to 
        be provided as a dict with net_sta keys.
        :param sta_coords: dict of station coords. sta[net_sta] = [lat,lon]
        :type sta_coords: dict
        :param extent: map boundaries. [min_lon, max_lon, min_lat, max_lat]. If
            no extent provided, get the extent from the station coordinates.
        :type extent: List
        :param buffer: Distance in degrees to add to the plot borders. Useful 
            when extent is None.
        :type buffer: float
        :param phase_list: List of all phase identifiers to use in generating
            the plot
        :type phase_list: List
        :param projection: Cartopy projection to use.
        :type projection: cartopy.crs.Projection
        :param max_duration: Maximum time allowed in the colorbar. If None, 
            use the maximum arrival time from Event.ttimes
        :type max_duration: int
        :param outfile: Filename to save image. If None, show the image instead.
        :type outfile: str
        """
        if not self.ttimes:
            self.calc_ttimes()
        times = [i[3] for i in self.ttimes if i[1] in phase_list]
        stations = [i[0] for i in self.ttimes if i[1] in phase_list]
        if not self.sta_coords and not sta_coords:
            raise ValueError("No Station Coordinates found in instance")
        if sta_coords:
            self.add_station_coords(sta_coords)
        coords = []
        for i in stations:
            coords.append(self.sta_coords[i])

        # set maximum time for colormap if max_duration is not explicity set
        if not max_duration:
            max_duration = max(times)

        # Set coordinates for map extent if extent not explicitly set
        # and add a quarter degree buffer
        if not extent:
            min_lon = min([float(i[1]) for i in coords]) - 0.25
            max_lon = max([float(i[1]) for i in coords]) + 0.25
            min_lat = min([float(i[0]) for i in coords]) - 0.25
            max_lat = max([float(i[0]) for i in coords]) + 0.25
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

        ax.set_title(f"Mag {self.mag} Event on {self.origin_time}")
        ax.plot(self.longitude, self.latitude, marker="*", color='yellow',
                markersize=15, linestyle='-', markeredgecolor='k', 
                transform=ccrs.Geodetic())
        cmap = cm.get_cmap('viridis')
        for i,val in enumerate(times):
            img = ax.scatter(float(coords[i][1]), float(coords[i][0]), marker='v',
                    c=val, cmap=cmap, norm=colors.Normalize(vmin=0, 
                    vmax=max_duration), s=175, zorder=10, edgecolors='k',
                    transform=ccrs.Geodetic())
        plt.colorbar(img, ax=ax, label="Arrival Time (s)")

        if outfile:
            plt.savefig(outfile)
        else:
            plt.show()


    def __repr__(self):
        return f"{self.origin_time} event"
    
