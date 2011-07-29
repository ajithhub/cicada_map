def get_gps_coords(exif_data):
    lat_list  = exif_data['GPS GPSLatitude']
    long_list = exif_data['GPS GPSLongitude']
    lat_ref   = exif_data['GPS GPSLatitudeRef']
    long_ref  = exif_data['GPS GPSLongitudeRef']

    if str(lat_ref) == 'N':
        lat_ref = 1.0
    else:
        lat_ref = -1.0

    if str(long_ref) == 'E':
        long_ref = 1.0
    else:
        long_ref = -1.0

    if len(lat_list.values) != 3 or len(long_list.values) !=3:
        return (0.0,0.0)

    return (ratios_to_float(lat_list.values) * lat_ref,
            ratios_to_float(long_list.values) * long_ref)

def ratios_to_float(ratio_list):
    result = 0.0
    ratio = ratio_list.pop()
    result += (ratio.num/1.0)/(ratio.den/1.0)/60.0/60.0
    ratio = ratio_list.pop()
    result += (ratio.num/1.0)/(ratio.den/1.0)/60.0
    ratio = ratio_list.pop()
    result += (ratio.num/1.0)/(ratio.den/1.0)
    return result
