import math
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

def calc_dist_geo(x1: Union[List, np.array], x2: Union[List, np.array],
                  a: float=6378137.0, f: float=1/298.257223563):
    """
    Calculate great-circle distance using the Vincenty formula. Obspy
    implementation [https://docs.obspy.org/_modules/obspy/geodetics/base.html#calc_vincenty_inverse]
    :param x1: First [lat, lon] pair
    :type x1: List
    :param x2: Second [lat, lon] pair
    :type x2: List
    :param a: Semi-major axis (WGS84 default)
    :type a: float
    :param f: flattening (WGS84 default)
    :type f: float
    :param max_iter: Maximum number of iterations for the inversion
    :type max_iter: int
    :param tol: convergence value
    :type tol: float
    :return: Great-circle distance in m, azimuth A->B in degrees, 
        azimuth B->A in degrees
    :rtype: np.float64
    """
    b = a * (1 - f)  # semiminor axis

    if math.isclose(x1[0], x2[0]) and math.isclose(x1[1], x2[1]):
        return 0.0, 0.0, 0.0

    # convert latitudes and longitudes to radians:
    lat1 = math.radians(x1[0])
    lon1 = math.radians(x1[1])
    lat2 = math.radians(x2[0])
    lon2 = math.radians(x2[1])

    tan_u1 = (1 - f) * math.tan(lat1)
    tan_u2 = (1 - f) * math.tan(lat2)

    u_1 = math.atan(tan_u1)
    u_2 = math.atan(tan_u2)

    dlon = lon2 - lon1
    last_dlon = -4000000.0  # an impossible value
    omega = dlon

    # Iterate until no significant change in dlon or iterlimit has been
    # reached (http://www.movable-type.co.uk/scripts/latlong-vincenty.html)
    iterlimit = 100
    try:
        while (last_dlon < -3000000.0 or dlon != 0 and
               abs((last_dlon - dlon) / dlon) > 1.0e-9):
            sqr_sin_sigma = pow(math.cos(u_2) * math.sin(dlon), 2) + \
                pow((math.cos(u_1) * math.sin(u_2) - math.sin(u_1) *
                     math.cos(u_2) * math.cos(dlon)), 2)
            sin_sigma = math.sqrt(sqr_sin_sigma)

            cos_sigma = math.sin(u_1) * math.sin(u_2) + math.cos(u_1) * \
                math.cos(u_2) * math.cos(dlon)
            sigma = math.atan2(sin_sigma, cos_sigma)
            sin_alpha = math.cos(u_1) * math.cos(u_2) * math.sin(dlon) / \
                sin_sigma

            sqr_cos_alpha = 1 - sin_alpha * sin_alpha
            if math.isclose(sqr_cos_alpha, 0):
                # Equatorial line
                cos2sigma_m = 0
            else:
                cos2sigma_m = cos_sigma - \
                    (2 * math.sin(u_1) * math.sin(u_2) / sqr_cos_alpha)

            c = (f / 16) * sqr_cos_alpha * (4 + f * (4 - 3 * sqr_cos_alpha))
            last_dlon = dlon
            dlon = omega + (1 - c) * f * sin_alpha * \
                (sigma + c * sin_sigma *
                    (cos2sigma_m + c * cos_sigma *
                        (-1 + 2 * pow(cos2sigma_m, 2))))

            iterlimit -= 1
            if iterlimit < 0:
                # iteration limit reached
                raise StopIteration
    except ValueError:
        # usually "math domain error"
        raise StopIteration

    u2 = sqr_cos_alpha * (a * a - b * b) / (b * b)
    _a = 1 + (u2 / 16384) * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    _b = (u2 / 1024) * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    delta_sigma = _b * sin_sigma * \
        (cos2sigma_m + (_b / 4) *
            (cos_sigma * (-1 + 2 * pow(cos2sigma_m, 2)) - (_b / 6) *
                cos2sigma_m * (-3 + 4 * sqr_sin_sigma) *
                (-3 + 4 * pow(cos2sigma_m, 2))))

    dist = b * _a * (sigma - delta_sigma)
    alpha12 = math.atan2(
        (math.cos(u_2) * math.sin(dlon)),
        (math.cos(u_1) * math.sin(u_2) -
            math.sin(u_1) * math.cos(u_2) * math.cos(dlon)))
    alpha21 = math.atan2(
        (math.cos(u_1) * math.sin(dlon)),
        (-math.sin(u_1) * math.cos(u_2) +
            math.cos(u_1) * math.sin(u_2) * math.cos(dlon)))

    if alpha12 < 0.0:
        alpha12 = alpha12 + (2.0 * math.pi)
    if alpha12 > (2.0 * math.pi):
        alpha12 = alpha12 - (2.0 * math.pi)

    alpha21 = alpha21 + math.pi

    if alpha21 < 0.0:
        alpha21 = alpha21 + (2.0 * math.pi)
    if alpha21 > (2.0 * math.pi):
        alpha21 = alpha21 - (2.0 * math.pi)

    # convert to degrees:
    alpha12 = alpha12 * 360 / (2.0 * math.pi)
    alpha21 = alpha21 * 360 / (2.0 * math.pi)

    return dist, alpha12, alpha21

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
