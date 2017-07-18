import requests
import json
import calendar
from datetime import datetime

#Read the original JSON
path_input_file = 'calificaciones_filtrado.JSON'

with open(path_input_file, "r") as input_file:
    data = json.load(input_file)

result = {}
result['type'] = data['type']
result['crs'] = data['crs']
result['features'] = []

#Keys to associate with each search
clave = {
    'PID': ("train_station"),
    'GTR': ("bus_station"),
    'GSP': ("hospital"),
    'TER': ("department_store"), #Other type: shopping_mall
    'EDA': ("park"), #Other type: gym, stadium
}
for feature in data['features']:
    y = str(feature['geometry']['coordinates'][0])
    x = str(feature['geometry']['coordinates'][1])
    cal = clave.get(feature['properties']['califi'], ("")) #Make the relation with the key
    r=requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+x+','+y+'&rankby=distance&distance=200&type='+str(cal)+'&key=AIzaSyAzWvwOz_45NBGqSlgLMj8zWnYNk76QcjI') #Request to API Google Places

    #'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+x+','+y+'&radius=500&type='+str(cal)+'&key=AIzaSyAzWvwOz_45NBGqSlgLMj8zWnYNk76QcjI'      Other possible request, focusing on the radio

    data2=json.loads(r.content.decode("utf8")) #JSON generated by the API request

    for out in data2['results']:
        z = str(out['name']+' '+out['vicinity'])
        print("\n Name: "+ z )
        break;
    
    feature['properties']['nombre'] = z #Add the 'name' property
    result['features'].append(feature)

#Write the output file
path_output_file = 'calificaciones_filtrado.JSON'

with open(path_output_file, "w") as output_file:
    json.dump((result), output_file, indent = 3)





