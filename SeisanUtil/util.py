from typing import List, Union, Dict

import numpy as np

def least_squares_bf(x: np.array, y: np.array):
    """ 
    Calculate the least squares best fit line for two data arrays.
    :param x: x-values
    :type x: np.array
    :param y: y-values
    :param y: np.array
    :returns: Tuple of y values for the line, the slope, and the intercept value
    :rtype: tuple
    """
    if isinstance(x, list) or isinstance(y, list):
        x = np.array(x)
        y = np.array(y)
    x_bar = x.mean()
    y_bar = y.mean()
    slope = np.sum((x-x_bar)*(y-y_bar))/np.sum((x-x_bar)**2)
    b = y_bar - slope*x_bar
    return (slope*x+b, slope, b)

def calc_dist(x1: Union[List, np.array], x2: Union[List, np.array]):
    """ 
    Calculate basic euclidean distance between two coordinates (degrees) and 
    return the distance in km.
    :param x1: First [lat,lon] pair
    :type x1: List
    :param x2: Second [lat,lon] pair
    :type x2: List
    :return: Euclidean distance between the two points, in km.
    :rtype: np.float64
    """
    return np.sqrt((x1[0]-x2[0])**2 + (x1[1]-x2[1])**2) * 111.11

def read_station_coords(coord_file: str, delim: bool =None, sta_col: int =1, 
                        lat_col:int =2, lon_col:int =3) -> Dict[str, List]:
    """
    Read file that contains station coordinates. 
    :param coord_file: File name of station coordinates
    :type coord_file: str
    :param delim: Delimiter character. Defaults to whitespace
    :type delim: str
    :param sta_col: Column (1-indexed) to read station name
    :type sta_col: int
    :param lat_col: Column (1-indexed) to read latitude
    :type lat_col: int
    :param lon_col: Column (1-indexed) to read longitude
    :type lon_col: int
    :return: Dictionary of station names with [lat, lon] values
    :rtype: dict
    """
    sta_coords = {}
    with open(coord_file, 'r') as f:
        for line in f.readlines():
            if delim:
                split_line = line.split(delim)
            else:
                split_line = line.split()
            sta_lat = float(split_line[lat_col-1])
            sta_lon = float(split_line[lon_col-1])
            # Strip potential whitespace from station name
            sta_name = split_line[sta_col-1].strip()
            sta_coords[sta_name] = [sta_lat, sta_lon]
    return sta_coords
