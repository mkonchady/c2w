#*-----------------------------------------------------
# Download json files from the cycle to work website
# Output: A set of JSON files in a ./json directory
#*-----------------------------------------------------
import requests

START_FACILITY = 0
END_FACILITY = 500
IMPORT_DIR = "../json/"
for i in range (START_FACILITY, END_FACILITY):
    url = "https://cycleto.work/api/v1/public/routes?facility_id=" + str(i)
    r = requests.get(url, allow_redirects=True)
    if (len(r.content) > 2):
        open(IMPORT_DIR + "route_" + str(i) + ".json", 'wb').write(r.content)
    print ("Finished file: " + str(i))
