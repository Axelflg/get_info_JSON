import requests
import json
import re
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

# Create a new Firefox session
capabilities = DesiredCapabilities.FIREFOX.copy()
capabilities['marionette'] = False
driver = webdriver.Firefox(capabilities=capabilities)
driver.implicitly_wait(10)

#--------------------------------------- LOOKTIME -------------------------------------------------------#
# DESCRIPTION: Get the time (as a string) that a person spend in a place through Selenium
# PARAMETERS: 
#    INPUT: name: Name from a place with vicinity as a result from the request to the Google Places API
#    OUTPUT: tiempo: Average time that a person spends in a place (Google's query)
#--------------------------------------------------------------------------------------------------------#

def looktime(name):
    # Navigate to the application home page
    driver.get('https://www.google.com')
    search_field = driver.find_element_by_name('q')
    search_field.clear()
    print('looktime')
    print(name)
    # Enter search keyword and submit
    search_field.send_keys(name)
    search_field.submit()

    # Currently on result page using find_elements_by_xpath method
    # Exception in case don't find the time
    try:
        tiempo = driver.find_element_by_xpath("//div[@class='_B1k']/b").text
        if len(tiempo) != 0:
            return tiempo
    except NoSuchElementException:
        return False

#--------------------------------------- GET_TIME -------------------------------------------------------#
# DESCRIPTION: Tranform the time as a string into an integer (through regular expressions) and get
#              the average time (in minutes)
# PARAMETERS: 
#    INPUT: tiempo: Average time as a string that a person spends in a place (Google's query)
#					This is an output from the LOOKTIME function
#    OUTPUT: fminutos: Average time in minutes as an integer
#--------------------------------------------------------------------------------------------------------#	

def get_time(tiempo):    
    fminutos=0
    count=0
    # Get minutes
    minutos = re.findall(r'\b\d+\bminutos|\d+-\d+\b|\d+\b min', tiempo)
    if minutos:
        if (str(minutos[0])).find('-') >= 1 :
            min1,min2=minutos[0].split("-")
            fminutos=int(min1)+int(min2)
            count=count+2
        else:
            minutos2=[int (m) for m in minutos[0].split() if m.isdigit()]
            fminutos=fminutos+int(minutos2[0])
            count=count+1
    # Get hours
    tiempo = tiempo.replace(",",".")
    horas = re.findall(r'\b\d+.\d+\b horas|\b\d+.\d+\b h|\b\d+\b horas|\b\d+\b h', tiempo)
    horas2=[]
    if horas:
        for t in horas[0].split():
            try:
                horas2.append(float(t))
            except ValueError:
                pass
        fminutos=fminutos+(int(horas2[0]*60))
        count=count+1
	# Get the average in case have the time more than once
    if count >= 2:
        fminutos=fminutos/2
    horas2.clear()
	# Take back the time in minutes
    return fminutos

#------------------------------------------ MAIN --------------------------------------------------------#
# DESCRIPTION: Add to the puntos_de_interes.json file the name and the average time in minutes that
# 			   a person spends in a point of interest
#
# INPUT FILE: puntos_de_interes.json
#		      This file was generated by data_processing.py program and already contains the 
#			  Valencia's points of interest with population, traffic and tweets
#
# OUTPUT FILE: puntos_de_interes.json
#			   Update of the input file
#--------------------------------------------------------------------------------------------------------#

def main():
    # Read the original JSON
    path_input_file = 'puntos_de_interes.JSON'

    with open(path_input_file, "r") as input_file:
        data = json.load(input_file)

    result = {}
    result['type'] = data['type']
    result['crs'] = data['crs']
    result['features'] = []

    # Keys to associate with each search
	# Google Place API gives a list of types, on the other hand the accuracy of the results depends of
	# the choice from the types
    clave = {
        'PID': ("train_station"),
        'GTR': ("bus_station"),
        'GSP': ("hospital"),
        'TER': ("shopping_mall"),  # Other type: department_store
        'EDA': ("park"),  # Other type: gym, stadium
    }
    cont=0
    for feature in data['features']:
        y = str(feature['geometry']['coordinates'][0])
        x = str(feature['geometry']['coordinates'][1])
        cal = clave.get(feature['properties']['califi'], (""))  # Make the relation with the key
        # Request to Google Places API with a distance of 20 meters from the point of interest
        r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+x+','+y+'&rankby=distance&distance=20&type='+str(cal)+'&key=AIzaSyBydM3PpubE1x3_Et1e_ApoFRujEvbUer8')  
        # Other possible request, focusing on the radio
	    # 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+x+','+y+'&radius=500&type='+str(cal)+'&key=AIzaSyCAJQUnW6GpmM5PmDa22kJuNFtOrwJTHhI'      
	    
        # a JSON generated by the API request
        data2 = json.loads(r.content.decode("utf8"))
        
        for out in data2['results']:
			#Get the first 5 results for each request to the Google Places API
            if cont <= 4 :
				# We only need the name and the vicinity to get the time with LOOKTIME function
                z = str(out['name'] + ' ' + out['vicinity'])
                print(z)
                time = looktime(z)
                if time:
                    time = get_time(time)
                    break
                else:
                    cont = cont +1
                    continue
            else:
                z = str(data2['results'][0]['name'] + ' ' + data2['results'][0]['vicinity']) #In case thata any of the firts five results have time, by default sets the first one
                time=0
        
        #Update the puntos_de_interes.json file
        feature['properties']['nombre'] = z  # Add the 'nombre' property   
        feature['properties']['tiempo_medio'] = time  # Add the 'tiempo_medio' property
		
        # Screen output to view program execution
        print("\n Name: " + z)
        print("\n Tiempo: " + str(time))
        result['features'].append(feature)
        z = ""
        time=""
        cont=0

    # Write the output file
    path_output_file = 'puntos_de_interes.JSON'

    with open(path_output_file, "w") as output_file:
        json.dump((result), output_file, indent=3)
        
    driver.quit()
if __name__ == "__main__":
    main()
