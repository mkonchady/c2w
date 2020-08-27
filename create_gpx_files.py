#*--------------------------------------------------------------------------
# create GPX files from downloaded json files stored in the json directory
#*--------------------------------------------------------------------------
import json
import os
import os.path
from os import path
import geopy.distance

# constants
START_FACILITY = 0
END_FACILITY = 500
JSON_DIR = "../data/json/"
GPX_DIR = "../data/gpx/"

# Limits
MAX_LOCATION_DISTANCE = 1.0    # kms.
MIN_LOCATION_DISTANCE = 0.025    # kms.

# Latitude / Longitude limits
LOW_LAT = 12.885707
HIGH_LAT = 13.1333
LOW_LON = 77.4749
HIGH_LON = 77.716

FAR = 0     # constants for distance comparison
CLOSE = 1
OK = 2

START_TRACK = "  <trk>\n   <trkseg>\n"
END_TRACK = "   </trkseg>\n  </trk>\n </gpx>\n"
GPX_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n <gpx>\n  <metadata>\n"

# Return FAR, CLOSE, or OK for the distance between the two locations
def get_distance_code(loc1, loc2):
    if (loc1 == None or loc2 == None):
        return OK
    distance = geopy.distance.geodesic(loc1, loc2).km   # get the distance in kms.
    if (distance > MAX_LOCATION_DISTANCE):
        return FAR
    if (distance < MIN_LOCATION_DISTANCE):
        return CLOSE
    return OK

# check if the location is within limits
def invalid_location(locations):
    for location in locations:
        lat = location[0]
        lon = location[1]
        if (lat < LOW_LAT or lat > HIGH_LAT or lon < LOW_LON or lon > HIGH_LON):
            return True
    return False

# write out the gpx file
def dump_file(header_lines, track_lines, fileno):
    if (len(header_lines) == 0 or len(track_lines) == 0):
        return fileno
    fileno = fileno + 1
    filename = DIR + "/r" + str(fileno) + ".gpx"
    f = open (filename, "w")
    for header_line in header_lines:
        f.write(header_line)
    for track_line in track_lines:
        f.write(track_line)
    f.close()
    print ("processed " + str(filename))
    return fileno

#*---------------------------------------------
#*- Main Section
#*---------------------------------------------
for FACILITY_ID in range (START_FACILITY, END_FACILITY):
    JSON_FILE = JSON_DIR + "route_" + str(FACILITY_ID) + ".json"
    if not path.exists(JSON_FILE):
        continue

    with open(JSON_FILE) as f:          # read the JSON file for the facility
        data = json.load(f)

    DIR = GPX_DIR + str(FACILITY_ID)   # create a GPX directory for the facility
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    # parse the JSON file and create a GPX file
    fileno = 0
    prev_location = None
    num_far_locations = 0
    for dict in data:   
        header_lines = []
        track_lines = []
        header_lines.append(GPX_HEADER)
        for key in dict:
            if (key != "map"):
                if (key == "date"):
                    header_lines.append("    <time>" + str(dict[key]) + "</time>\n")
                else:
                    header_lines.append("    <" + key + ">" + str(dict[key]) + "</" + key + ">\n")
            else:
                locations = dict[key]
                if (invalid_location(locations)):     # check if all the locations in the route 
                    continue                          # are within city limits
                header_lines.append("   </metadata>\n")
                track_lines.append(START_TRACK)
                for location in locations:
                    dist_code = get_distance_code(prev_location, location)
                    if (dist_code == CLOSE):    # skip close locations
                        continue
                    if (dist_code == FAR):      # if too far, start a new file
                        print (JSON_FILE + " Location: " + str(location) + " Prev: " + str(prev_location))
                        num_far_locations = num_far_locations + 1
                        if (len(track_lines) > 1):
                            track_lines.append(END_TRACK)
                            fileno = dump_file(header_lines, track_lines, fileno)
                            track_lines = []
                            track_lines.append(START_TRACK)
                    # if distance is OK, append to the list
                    track_lines.append("     <trkpt lat=\"" + str(location[0]) + "\" lon=\"" + str(location[1]) + "\"/>\n")
                    prev_location = location
                track_lines.append(END_TRACK)
        fileno = dump_file(header_lines, track_lines, fileno)
        
    print ("Finished facility: " + str(FACILITY_ID))
print ("Number of far locations: " + str(num_far_locations))
