import numpy as np

def least_squares(x: np.array, y: np.array):
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
        y = np.array(x)
    x_bar = x.mean()
    y_bar = y.mean()
    slope = np.sum((x-x_bar)*(y-y_bar))/np.sum((x-x_bar)**2)
    b = y_bar - slope*x_bar
    return (slope*x+b, slope, b)

def calc_dist(x1, x2):
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