import os

import click

from SeisanUtil.read import read_sfile
from SeisanUtil.util import read_station_coords


@click.group(no_args_is_help=True)
@click.argument("sfile")
@click.option("-f", "--format", help="What nordic format is the Sfile. Valid "
              "options are 1 or 2.", default=1)                               
@click.pass_context
def main(ctx, sfile: str=None, format: int=1):
    """
    CLI addition to SeisanUtil to allow quick analysis of single Sfiles.  If no
    sfile provided, searches the current directory for a file called 
    `eev.cur.sfile`. This file is generally created by Seisan's eev program
    in the Seisan WOR directory.
    """
    if not sfile:
        print("No provided Sfile, trying eev.cur.sfile in the current " 
              "directory")
        with open("eev.cur.sfile", 'r') as f:
            sfile = f.read().strip()
    
    ev = read_sfile(sfile, format=format)
    ctx.obj = {"ev": ev}
    


@main.command("ttplot", help="Plot a travel time plot from the provided Sfile. "
                 "By default, seperate P and S waves by color.")
@click.option("--sep_phase", is_flag=True, default=True, help="Plot all arrival " 
            "times as one color [False], or separate phases by color based on "
            "phase_list.")
@click.option("-f", "--filename", help="Write plot to this filename.")
@click.pass_context
def ttplot(ctx, sep_phase, filename):
    ev = ctx.obj["ev"]
    if not ev:
        raise RuntimeError("No Sfile provided. Please add an Sfile or run "
                           "program from the WOR directory.")
    ev.ttime_plot(sep_phase=sep_phase, outfile=filename)
    

@main.command("ttmap", help="Create a map with the event and station locations. "
             "Stations can be color coded by travel time.")
@click.option("-e", "--extent", nargs=4, type=float,
              help="Extent for map regions given in a list "
                   "of min_lon, max_lon, min_lat, max_lat. Ex: -e -90 -80 30 "
                   "40")
@click.option("-b", "--buffer", help="Buffer distance around the edge of the " 
            "map. Useful when not specifying --extent.", type=float)
@click.option("-f", "--filename", help="Write map to this filename")
@click.option("-c", "--sta_coords", help="File containing station coordinates "
            "for this event.", required=True)
@click.option("-d", "--max_duration", help="Maximum travel time (s) to plot.")
@click.pass_context
def ttmap(ctx, extent, buffer, filename, sta_coords, max_duration):
    ev = ctx.obj["ev"]
    if not ev:
        raise RuntimeError("No Sfile provided. Please add an Sfile or run the "
                           "program from the WOR directory.")
    coords = read_station_coords(sta_coords)
    # build kwarg dict to expand in call to ttime_map to preserve ev.ttime_map
    # defaults
    kwarg = {}
    kwarg["sta_coords"] = coords
    if extent:
        extent = [extent[0], extent[1], extent[2], extent[3]]
        kwarg['extent'] = extent
    if buffer:
        kwarg['buffer'] = buffer
    if filename:
        kwarg['outfile'] = filename
    if max_duration:
        kwarg['max_duration'] = max_duration

    ev.ttime_map(**kwarg)

@main.command("calc_mag", help="Calculate the defined magnitude for this "
              "event. This command will take any keyword arguments associated "
              "`SeisanUtil.Event.calc_mag`. "
              "Ex. seisanutil calc_mag min_dist=0 max_dist=800"
              " Parameters must be set with the an equal sign separating the "
              "keyword argument and the value.  If the keyword 'f' is used, "
              "calc_mag will import a single function(called 'mag') from the file. "
              "Ex. seisanutil calc_mag f=localmag.py will import a function "
              "called mag from the localmag.py file.  Remaining arguments "
              "will be passed to this function\n.  By default, station coords " 
              "must also be provided via the sta_coords=staCoordFile.txt "
              "However, if using a custom function this may not be needed." )
@click.argument("mag_params", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def calc_mag(ctx, mag_params):
    ev = ctx.obj["ev"]
    if not ev:
        raise RuntimeError("No Sfile provided. Please add an Sfile or run the "
                           "program from the WOR directory.")
    kw = {}
    for i in mag_params:
        k,v = i.split("=")
        kw[k] = v
    if "sta_coords" in kw:
        kw["sta_coords"] = read_station_coords(kw["sta_coords"])
    if "f" in kw:
        from importlib.util import spec_from_file_location, module_from_spec
        if "/" in kw["f"]:
            raise NotImplementedError("Files outside of os.getcwd() are not "
                                      "currently supported")
        fn_name = kw["f"]
        spec = spec_from_file_location(f"{fn_name[:-3]}", f"{os.getcwd()}/{fn_name}")
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
        del kw["f"]
        ev.calc_mag(func=mod.mag, **kw)
    else:
        ev.calc_mag(**kw)
    print(f"Magnitude: {ev.mag}")

def run():
    main(obj={})