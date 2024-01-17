import requests
from pprint import pprint

url = "https://niai-api.mrahhal.net/api/search"
param = {'q':'勉強'}
response = requests.get(url,params=param, headers={'accept': 'text/plain'})
data = response.json()
pprint(data)