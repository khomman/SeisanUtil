from datetime import datetime
from SeisanUtil.event import Event

def read_sfile(path: str, format: int =1, read_arrivals: bool =True) -> Event:
    """ Parse an Sfile from Seisan and return an Event instance
    :param path: path to the Sfile to parse
    :type path: str
    :param format: Read Sfile as either nordic or nordic2. Nordic2 was common
        with seisan version < 12.0
    :type format: int
    :param read_arrivals: Read arrival information from Sfile
    :type read_arrivals: bool
    :return: Event instance
    :rtype: Event
    """
    if format != 1 and format != 2:
        raise ValueError("read_sfile: format must be 1 or 2")
    
    event = Event()
    with open(path, 'r') as f:
        for line in f.readlines():
            # Skip any blank lines
            if not line.strip():
                continue
            if line[-3:] == "EC3":
                type_line = "EC3"
            elif line[-6:] == "MACRO3":
                type_line == "MACRO3"
            else:
                type_line = line[79]

            if type_line == '1':
                hyp_info = _parse_type_1(line)
                event.update_from_dict(hyp_info)
            elif type_line == '2':
                macro_info = _parse_type_2(line)
                event.update_from_dict(macro_info)
            elif type_line == '3':
                comment = _parse_type_3(line)
                event.update_from_dict(comment)
            elif type_line == ' ' and read_arrivals and format == 1:
                if event.origin_time:
                    date = event.origin_time.strftime("%Y-%m-%d")
                    phase_info = _parse_type_phase_nordic(line, date=date)
                else:
                    phase_info = _parse_type_phase_nordic(line)
                event.add_arrivals_from_dict(phase_info)
            elif type_line == ' ' and read_arrivals and format == 2:
                if event.origin_time:
                    date = event.origin_time.strftime("%Y-%m-%d")
                    phase_info = _parse_type_phase_nordic2(line, date=date)
                else:
                    phase_info = _parse_type_phase_nordic2(line)
                event.add_arrivals_from_dict(phase_info)
            elif type_line == '6':
                wff = _parse_type_6(line)
                event.update_from_dict(wff)
            elif type_line == 'E':
                error_info = _parse_type_E(line)
                event.update_from_dict(error_info)
            elif type_line == 'F':
                fp_info = _parse_type_F(line)
                event.update_from_dict(fp_info)
            elif type_line == 'H':
                hyp_info = _parse_type_H(line)
                event.update_from_dict(hyp_info)
            elif type_line == 'I':
                id_info = _parse_type_I(line)
                event.update_from_dict(id_info)
            elif type_line == 'M':
                mt_info = _parse_type_M(line)
                event.update_from_dict(mt_info)
            elif type_line == 'P':
                pic = _parse_type_P(line)
                event.update_from_dict(pic)
            elif type_line == 'S':
                spec_info = _parse_type_S(line)
                event.update_from_dict(spec_info)
            elif type_line == "EC3":
                exp_info = _parse_type_EC3(line)
                event.update_from_dict(exp_info)
            elif type_line == "MACRO3":
                macro_info = _parse_type_macro(line)
                event.update_from_dict(macro_info)
    event.sfile = path
    return event

def _parse_type_1(line: str) -> dict:
    """Parse a nordic "Type 1" line which contains information about the 
    hypocenter
    """
    ev_info = {"year": line[1:5], "month": line[6:8], "day": line[8:10],
               "hour": line[11:13], "minute": line[13:15],
               "second": line[16:20], "latitude": line[23:30],
               "longitude": line[30:38], "depth": line[38:43],
               "n": line[48:51], "rms": line[51:55], "mag": line[55:59]}
    int_keys = ["year", "month", "day", "hour", "minute", 'n']
    float_keys = ["second", "latitude", "longitude", "depth", "rms", "mag"]
    for k,v in ev_info.items():
        ev_info[k] = v.strip()
    for key in int_keys:
        if ev_info[key].strip():
            ev_info[key] = int(ev_info[key])
    for key in float_keys:
        if ev_info[key].strip():
            ev_info[key] = float(ev_info[key])
    date = f"{ev_info['year']}-{ev_info['month']:02}-{ev_info['day']:02}"
    time = f"{ev_info['hour']:02}:{ev_info['minute']:02}:{ev_info['second']:02}"
    origin_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S.%f")
    ev_info['origin_time'] = origin_time
    if line[43] == "F":
        ev_info["fixed_depth"] = True
    else:
        ev_info["fixed_depth"] = False
    return ev_info

def _parse_type_2(line: str) -> dict:
    """Parse a nordic Type 2 line which contains macroseismic information"""
    pass

def _parse_type_3(line:str) -> dict:
    """ Parse a nordic Type 3 line which contains comments"""
    ev_info = {}
    ev_info['comment'] = line[1:80]
    return ev_info

def _parse_type_phase_nordic2(line:str, date:str=None) -> dict:
    """ Parse a nordic phase line. Acceptable for nordic2 format"""
    arr = {"sta": line[1:6], "cmp": line[6:9], "Net": line[10:12],
           "loc":line[12:14], "qual": line[15],
           "phase": line[16:24], "wgtind": line[24],
           "arr_h": line[26:28], "arr_m": line[28:30],
           "arr_s": line[31:37], "param1": line[37:44],
           "param2": line[44:50], "agency": line[51:54], "op": line[55:58],
           "ain": line[59:63], "tres": line[63:68], "dist": line[70:75],
           "az": line[76:79]}
    int_keys = ["arr_h", "arr_m"]
    float_keys = ["per", "amp", "arr_s", "ain", "dist", "trex", "az"]
    # deal with empty results
    for k,v in arr.items():
        arr[k] = v.strip()
    for key in int_keys:
        if arr[key]:
            arr[key] = int(arr[key])
    for key in float_keys:
        if arr[key]:
            arr[key] = float(arr[key])
    time = f"{arr['arr_h']:02}:{arr['arr_m']:02}:{arr['arr_s']:02}"
    if date:
        arr['arrtime'] = datetime.strptime(f"{date} {time}",
                                            "%Y-%m-%d %H:%M:%S.%f")
    else:
        arr['arrtime'] = datetime.strptime(time, "%H:%M:%S.%f")
    return arr

def _parse_type_phase_nordic(line: str, date:str =None) -> dict:
    """ Parse a nordic phase line. Acceptable for seisan pre v12.0"""
    arr = {"sta": line[1:6], "inst": line[6], "cmp": line[7],
           "qual": line[9], "phase": line[10:14], "wgtind": line[14],
           "pol": line[16], "arr_h": line[18:20], "arr_m": line[20:22],
           "arr_s": line[22:28], "amp": line[33:40],
           "per": line[41:45], "ain": line[56:60], "tres": line[63:68],
           "dist": line[70:75], "az": line[75:79]}
    int_keys = ["arr_h", "arr_m"]
    float_keys = ["per", "amp", "arr_s", "ain", "dist", "tres", "az"]
    for k,v in arr.items():
        arr[k] = v.strip()
    for key in int_keys:
        if arr[key]:
            arr[key] = int(arr[key])
    for key in float_keys:
        if arr[key]:
            arr[key] = float(arr[key])
    time = f"{arr['arr_h']:02}:{arr['arr_m']:02}:{arr['arr_s']:02}"
    if date:
        arr['arrtime'] = datetime.strptime(f"{date} {time}",
                                            "%Y-%m-%d %H:%M:%S.%f")
    else:
        arr['arrtime'] = datetime.strptime(time, "%H:%M:%S.%f")
    return arr

def _parse_type_6(line: str) -> dict:
    """ Parse type 6 line. Contains Waveform data file location/link"""
    return {"wf_location": line[1:79].strip()}

def _parse_type_E(line: str) -> dict:
    """ Parse Type E line. Contains Hypocenter error estimates"""
    ev_info = {"gap": line[5:8], "otime_err": line[14:20],
               "lat_err": line[23:30],
               "lon_err": line[31:38], "z_err": line[38:43]}
    for k,v in ev_info.items():
        if v.strip():
            ev_info[k] = float(v)
        else:
            ev_info[k] = ''
    return ev_info

def _parse_type_F(line: str) -> dict:
    """ Parse Type F line. Contains Fault plane solution"""
    ev_info = {
    "sdr_aki": line[1:30],
    "fp_err": line[30:45],
    "fp_fit_err": line[45:50],
    "sta_dist_ratio": line[50:55],
    "amp_ratio_fit": line[55:60],
    "n_bad_pol": line[60:62],
    "n_bad_amp": line[63:65],
    "agency_code": line[66:69],
    "fp_program": line[70:77],
    "soln_qual": line[77:78]}
    return ev_info

def _parse_type_H(line: str) -> dict:
    """ Parse Type H line. High accuracy hypocenter line"""
    return {}

def _parse_type_I(line: str) -> dict:
    """ Parse Type I line. Contains ID"""
    return {}

def _parse_type_M(line: str) -> dict:
    """ Parse Type M line. Contains moment tensor solution"""
    return {}

def _parse_type_P(line: str) -> dict:
    """ Parse Type P line. Contains picture file name"""
    return {}

def _parse_type_S(line: str) -> dict:
    """ Parse Type S line. Contains Spectral parameters. Seisan > v12.0"""
    return {}

def _parse_type_EC3(line: str) -> dict:
    """ Parse Type E13 and EC3 line. Contains Explosion information"""
    exp_info = {"ex_info": line[1:11], "ex_charge": line[12:22],
                "ex_extra_info": line[23:77]}
    return exp_info

def _parse_type_macro(line: str) -> dict:
    """ Parse Type macro3 line. Contains file name of macroseismic 
        observation
    """
    return {"macro_file": line.split()[0]}
