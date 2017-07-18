import requests
import json
import calendar
import re
from datetime import datetime

#Read the original JSON
path_input_file = 'calificaciones_filtrado.JSON'

with open(path_input_file, "r") as input_file:
    data = json.load(input_file)

result = {}
result['type'] = data['type']
result['crs'] = data['crs']
result['features'] = []

for feature in data['features']:
    tiempo=feature['properties']['tiempo']

    fminutos=0
    count=0
    #Get minutes
    minutos = re.findall(r'\b\d+\bminutos|\d+-\d+\b|\d+\b min', tiempo)
    if minutos:
        if (str(minutos[0])).find('-') >= 1 :
            min1,min2=minutos[0].split("-")
            fminutos=int(min1)+int(min2)
            count=count+1
        else:
            minutos2=[int (m) for m in minutos[0].split() if m.isdigit()]
            fminutos=fminutos+int(minutos2[0])
            count=count+1
    #Get hours
    horas = re.findall(r'\b\d+.\d+\b horas|\b\d+.\d+\b h|\b\d+\b horas|\b\d+\b h', tiempo)
    if horas:
        horas2=[]
        for t in horas[0].split():
            try:
                horas2.append(float(t))
            except ValueError:
                pass
        fminutos=fminutos+(int(horas2[0]*60))
        count=count+1
    if count >= 2:
        fminutos=fminutos/2
    feature['properties']['tiempo'] = fminutos
    result['features'].append(feature)

#Write the output file
path_output_file = 'calificaciones_filtrado.JSON'

with open(path_output_file, "w") as output_file:
    json.dump((result), output_file, indent = 3)





