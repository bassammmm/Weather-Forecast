
import geocoder
import requests
import json

g = geocoder.ip('me')
lat,lon = g.latlng


API_KEY = "cc75913f8e1dafdb317ff0d22c3825e3"

url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}"
req = requests.get(url)
data = json.loads(req.text)
print(data)

print(data["name"])
