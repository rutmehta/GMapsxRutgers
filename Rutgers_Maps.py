import math
import numpy
import googlemaps
import json
import requests
from datetime import datetime, timedelta
import heapdict

def stopsToSearch(stop):
    listOfDoubles = ["Allison Road Classrooms", "Science Building", "Werblin Main Entrance", "Weblin Recreation Center", "SoCam Apts (NB)", "SoCam Apts (SB)"]

    if stop in listOfDoubles:
        if stop == "Allison Road Classrooms":
            return ["Allison Road Classrooms", "Science Building"]
        elif stop == "Science Building":
            return ["Allison Road Classrooms", "Science Building"]
        elif stop == "Werblin Main Entrance":
            return ["Werblin Main Entrance", "Weblin Recreation Center"]
        elif stop == "Weblin Recreation Center":
            return ["Werblin Main Entrance", "Weblin Recreation Center"]
        elif stop == "SoCam Apts (NB)":
            return ["SoCam Apts (NB)", "SoCam Apts (SB)"]
        elif stop == "SoCam Apts (SB)":
            return ["SoCam Apts (NB)", "SoCam Apts (SB)"]
        else:
            return [stop]
    return [stop]
#load all bus stop coordinates
bus_stops = {}
with open("Bus_Stops_locations.txt") as f:
    for line in f:
        line = line.rstrip()
        lat, lng = tuple(next(f).split(", "))
        bus_stops[line] = (float(lat)), (float(lng))

# Get user input and store it in a variable
user_input_origin = input("Enter your origin address: ")
user_input_destination = input("Enter your destination address: ")

# Display the user input
print("This is your origin address: ", user_input_origin)
print("This is your destination address: ", user_input_destination)

gmaps = googlemaps.Client(key='AIzaSyAM-OL61bAhosULEJcT9sxONxjyw-bjo60')

geocode_result = gmaps.geocode(user_input_origin)
origin_lat = geocode_result[0]['geometry']['location']['lat']
origin_lng = geocode_result[0]['geometry']['location']['lng']

geocode_result = gmaps.geocode(user_input_destination)
dest_lat = geocode_result[0]['geometry']['location']['lat']
dest_lng = geocode_result[0]['geometry']['location']['lng']

closest_origin = heapdict.heapdict()
closest_destination = heapdict.heapdict()
now = datetime.now()
for stop, coordinates in bus_stops.items():
    leg_o = gmaps.directions((origin_lat, origin_lng), coordinates, mode="walking", departure_time=now)
    leg_d = gmaps.directions(coordinates, (dest_lat, dest_lng), mode="walking", departure_time=now)
    closest_origin[stop] = leg_o[0]['legs'][0]['distance']['value']
    closest_destination[stop] = leg_d[0]['legs'][0]['distance']['value']

url = "https://store.transitstat.us/passio_go/rutgers"  # website from transitstat.us

# Make an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Assuming `response` is the response object from a web request
    # columns = ['bus_id', 'line', 'lineCode', 'dest', 'stationID', 'stationName', 'actualETA', 'noETA']
    
    data = response.json()['trains']
    # print(data)
else:
    print(f"Error: Unable to retrieve data. Status code: {response.status_code}")

print(closest_origin.peekitem())
print(closest_destination.peekitem())
walkingArrivalTime = datetime.now() + timedelta(seconds=closest_origin.peekitem()[1])
# print(walkingArrivalTime)
closest_o = closest_origin.peekitem()[0]
closest_d = closest_destination.peekitem()[0]

routes = []
origin_stops = stopsToSearch(closest_o)
print(origin_stops)
destination_stops = stopsToSearch(closest_d)
print(destination_stops)

for bus in data:
    origin_included = False
    destination_included = False
    setOfETA = []
    for prediction in data[bus]['predictions']:
        ETA = datetime.fromtimestamp(prediction['actualETA']/1000)
        # print(bus, prediction['stationName'], ETA)
        if len(origin_stops) > 1:
            if prediction['stationName'] == origin_stops[0] or prediction['stationName'] == origin_stops[1]:
                origin_included = True
                setOfETA.append((prediction['stationName'], ETA))
        else:
            if prediction['stationName'] == closest_o:
                origin_included = True
                setOfETA.append((closest_o, ETA))
        if len(destination_stops) > 1:
            if prediction['stationName'] == destination_stops[0] or prediction['stationName'] == destination_stops[1]:
                destination_included = True
                setOfETA.append((prediction['stationName'], ETA))
        else:
            if prediction['stationName'] == closest_d or data[bus]['dest'] == closest_d:
                destination_included = True
                setOfETA.append((closest_d, ETA))
        # print(origin_included, destination_included)
    if origin_included and destination_included:
        routes.append((bus, data[bus]['line'], setOfETA))
totalTime = None
busToTake = None
# for route in routes:
# totalTime = heapdict.heapdict()    
# for route in routes:
#     a, b = route[2][0], route[2][1]
    
#     if a[0] == closest_o and a[1] > walkingArrivalTime and a[1] < b[1]:
#         totalTime[route[0]] = (b[1] - a[1]) + timedelta(seconds=leg_d[0]['legs'][0]['duration']['value'])
#     elif b[0] == closest_o and b[1] > walkingArrivalTime and b[1] < a[1]:
#         totalTime[route[0]] = (a[1] - b[1]) + timedelta(seconds=leg_d[0]['legs'][0]['duration']['value'])
        
# print(totalTime.peekitem())

print(routes)