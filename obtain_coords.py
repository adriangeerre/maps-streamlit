# Dependencies
import json
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

# Class
class CountryLocations():

	def create_countries_array(self, file):
		countries = []
		
		f = open(file, 'r')
		for line in f.readlines():
			countries.append(line.strip("\n"))
		f.close()
		
		return countries

	def init_geopy(self):
		geo = Nominatim(user_agent="Countries")
		return geo

	def get_location(self, countries):
		coor = {}
		geo = self.init_geopy()
		for country in countries:
			info = geo.geocode(country)
			if info != None:
				info = list(info)
				coor[country] = list(info[1])
			else:
				pass

		return coor

# Get coordinates
c = CountryLocations()
countries = c.create_countries_array("countries.txt")
d = c.get_location(countries)

# Save file as Json
with open('country_coords.json', 'w') as fp:
    json.dump(d, fp, sort_keys=True, indent=4)