import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException

import json
import calendar
from datetime import datetime

class HomePageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create a new Firefox session
        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities['marionette'] = False
        cls.driver = webdriver.Firefox(capabilities=capabilities)
        cls.driver.implicitly_wait(10)

        # navigate to the application home page
        cls.driver.get('https://www.google.com')

    def test_search_text_field(self):
        # Read the original JSON
        path_input_file = 'calificaciones_filtrado.JSON'

        with open(path_input_file, "r") as input_file:
            data = json.load(input_file)

        result = {}
        result['type'] = data['type']
        result['crs'] = data['crs']
        result['features'] = []

        for feature in data['features']:
            #find the textbox
            search_field = self.driver.find_element_by_name('q')
            search_field.clear()

            # enter search keyword and submit
            search_field.send_keys(str(feature['properties']['nombre']))
            search_field.submit()

            # currently on result page using find_elements_by_xpath method
            # exception in case don't find the time
            try:
                tiempo = self.driver.find_element_by_xpath("//div[@class='_B1k']/b").text
            except NoSuchElementException:
                tiempo = ""
            #Add the time property
            feature['properties']['tiempo'] = tiempo
            result['features'].append(feature)
            
        # Write the output file
        path_output_file = 'calificaciones_2017.JSON'

        with open(path_output_file, "w") as output_file:
            json.dump((result), output_file, indent=3)

    @classmethod
    def tearDownClass(cls):
        # close the browser window
        cls.driver.quit()

if __name__ == '__main__':
    unittest.main(verbosity=2)